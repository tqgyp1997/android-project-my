package com.xianyu.taskexecutor.network

import io.socket.client.IO
import io.socket.client.Socket
import io.socket.emitter.Emitter
import org.json.JSONObject
import timber.log.Timber
import java.net.URISyntaxException

/**
 * WebSocket连接管理器
 * 负责与分布式任务系统的实时通信
 * 创建时间: 2025-09-17
 */
class WebSocketManager private constructor() {
    
    companion object {
        @Volatile
        private var INSTANCE: WebSocketManager? = null
        
        fun getInstance(): WebSocketManager {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: WebSocketManager().also { INSTANCE = it }
            }
        }
    }
    
    private var socket: Socket? = null
    private var isConnected = false
    private var serverUrl = "http://192.168.0.153:1888" // 默认服务器地址
    private var deviceId = ""
    private var deviceName = ""
    
    // 事件监听器
    private val connectionListeners = mutableListOf<(Boolean) -> Unit>()
    private val taskListeners = mutableListOf<(JSONObject) -> Unit>()
    private val messageListeners = mutableListOf<(String, JSONObject?) -> Unit>()
    
    /**
     * 初始化WebSocket连接
     */
    fun initialize(serverUrl: String, deviceId: String, deviceName: String) {
        this.serverUrl = serverUrl
        this.deviceId = deviceId
        this.deviceName = deviceName
        
        Timber.d("初始化WebSocket: $serverUrl, 设备ID: $deviceId")
        
        try {
            val options = IO.Options().apply {
                timeout = 10000
                reconnection = true
                reconnectionAttempts = 5
                reconnectionDelay = 2000
            }
            
            socket = IO.socket(serverUrl, options)
            setupEventListeners()
            
        } catch (e: URISyntaxException) {
            Timber.e(e, "WebSocket URL格式错误: $serverUrl")
        }
    }
    
    /**
     * 设置事件监听器
     */
    private fun setupEventListeners() {
        socket?.apply {
            // 连接事件
            on(Socket.EVENT_CONNECT) {
                Timber.d("WebSocket连接成功")
                isConnected = true
                notifyConnectionListeners(true)
                registerDevice()
            }
            
            on(Socket.EVENT_DISCONNECT) {
                Timber.d("WebSocket连接断开")
                isConnected = false
                notifyConnectionListeners(false)
            }
            
            on(Socket.EVENT_CONNECT_ERROR) { args ->
                val error = if (args.isNotEmpty()) args[0].toString() else "未知错误"
                Timber.e("WebSocket连接错误: $error")
                isConnected = false
                notifyConnectionListeners(false)
            }
            
            // 设备注册响应
            on("register_success") { args ->
                if (args.isNotEmpty()) {
                    val data = args[0] as JSONObject
                    Timber.d("设备注册成功: ${data.optString("message")}")
                    notifyMessageListeners("register_success", data)
                }
            }
            
            // 新任务事件
            on("new_task") { args ->
                if (args.isNotEmpty()) {
                    val taskData = args[0] as JSONObject
                    Timber.d("收到新任务: ${taskData.optString("task_id")}")
                    notifyTaskListeners(taskData)
                }
            }
            
            // 取消任务事件
            on("cancel_task") { args ->
                if (args.isNotEmpty()) {
                    val data = args[0] as JSONObject
                    Timber.d("任务被取消: ${data.optString("task_id")}")
                    notifyMessageListeners("cancel_task", data)
                }
            }
            
            // 心跳确认
            on("heartbeat_ack") { args ->
                if (args.isNotEmpty()) {
                    val data = args[0] as JSONObject
                    Timber.v("心跳确认: ${data.optString("server_time")}")
                    notifyMessageListeners("heartbeat_ack", data)
                }
            }
            
            // 错误事件
            on("error") { args ->
                if (args.isNotEmpty()) {
                    val data = args[0] as JSONObject
                    val message = data.optString("message", "服务器错误")
                    Timber.e("服务器错误: $message")
                    notifyMessageListeners("error", data)
                }
            }
        }
    }
    
    /**
     * 连接到服务器
     */
    fun connect() {
        if (socket == null) {
            Timber.e("WebSocket未初始化，请先调用initialize()")
            return
        }
        
        if (isConnected) {
            Timber.d("WebSocket已连接")
            return
        }
        
        Timber.d("开始连接WebSocket...")
        socket?.connect()
    }
    
    /**
     * 断开连接
     */
    fun disconnect() {
        Timber.d("断开WebSocket连接")
        socket?.disconnect()
        isConnected = false
    }
    
    /**
     * 注册设备
     */
    private fun registerDevice() {
        val deviceInfo = JSONObject().apply {
            put("device_id", deviceId)
            put("device_name", deviceName)
            put("device_info", JSONObject().apply {
                put("type", "android")
                put("version", android.os.Build.VERSION.RELEASE)
                put("app_version", "1.0.0")
                put("model", android.os.Build.MODEL)
                put("manufacturer", android.os.Build.MANUFACTURER)
            })
        }
        
        Timber.d("注册设备: $deviceInfo")
        socket?.emit("device_register", deviceInfo)
    }
    
    /**
     * 发送心跳
     */
    fun sendHeartbeat() {
        if (!isConnected) return
        
        val heartbeatData = JSONObject().apply {
            put("device_id", deviceId)
            put("timestamp", System.currentTimeMillis())
        }
        
        socket?.emit("heartbeat", heartbeatData)
        Timber.v("发送心跳")
    }
    
    /**
     * 发送任务结果
     */
    fun sendTaskResult(taskId: String, result: JSONObject) {
        if (!isConnected) {
            Timber.e("WebSocket未连接，无法发送任务结果")
            return
        }
        
        val resultData = JSONObject().apply {
            put("task_id", taskId)
            put("result", result)
        }
        
        Timber.d("发送任务结果: $taskId")
        socket?.emit("task_result", resultData)
    }
    
    /**
     * 发送任务进度
     */
    fun sendTaskProgress(taskId: String, progress: Int, message: String) {
        if (!isConnected) return
        
        val progressData = JSONObject().apply {
            put("task_id", taskId)
            put("progress", progress)
            put("message", message)
        }
        
        socket?.emit("task_progress", progressData)
        Timber.v("发送任务进度: $taskId - $progress%")
    }
    
    /**
     * 添加连接状态监听器
     */
    fun addConnectionListener(listener: (Boolean) -> Unit) {
        connectionListeners.add(listener)
    }
    
    /**
     * 移除连接状态监听器
     */
    fun removeConnectionListener(listener: (Boolean) -> Unit) {
        connectionListeners.remove(listener)
    }
    
    /**
     * 添加任务监听器
     */
    fun addTaskListener(listener: (JSONObject) -> Unit) {
        taskListeners.add(listener)
    }
    
    /**
     * 移除任务监听器
     */
    fun removeTaskListener(listener: (JSONObject) -> Unit) {
        taskListeners.remove(listener)
    }
    
    /**
     * 添加消息监听器
     */
    fun addMessageListener(listener: (String, JSONObject?) -> Unit) {
        messageListeners.add(listener)
    }
    
    /**
     * 移除消息监听器
     */
    fun removeMessageListener(listener: (String, JSONObject?) -> Unit) {
        messageListeners.remove(listener)
    }
    
    /**
     * 通知连接状态监听器
     */
    private fun notifyConnectionListeners(connected: Boolean) {
        connectionListeners.forEach { it(connected) }
    }
    
    /**
     * 通知任务监听器
     */
    private fun notifyTaskListeners(taskData: JSONObject) {
        taskListeners.forEach { it(taskData) }
    }
    
    /**
     * 通知消息监听器
     */
    private fun notifyMessageListeners(event: String, data: JSONObject?) {
        messageListeners.forEach { it(event, data) }
    }
    
    /**
     * 获取连接状态
     */
    fun isConnected(): Boolean = isConnected
    
    /**
     * 更新服务器地址
     */
    fun updateServerUrl(newUrl: String) {
        if (serverUrl != newUrl) {
            serverUrl = newUrl
            if (isConnected) {
                disconnect()
                initialize(serverUrl, deviceId, deviceName)
                connect()
            }
        }
    }
}
