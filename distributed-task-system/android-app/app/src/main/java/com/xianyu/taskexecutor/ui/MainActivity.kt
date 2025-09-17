package com.xianyu.taskexecutor.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.provider.Settings
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import com.xianyu.taskexecutor.R
import com.xianyu.taskexecutor.databinding.ActivityMainBinding
import com.xianyu.taskexecutor.service.TaskExecutorService
import com.xianyu.taskexecutor.viewmodel.MainViewModel
import timber.log.Timber

/**
 * 主活动
 * 闲鱼任务执行器的主界面
 * 创建时间: 2025-09-17
 */
class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: MainViewModel
    
    companion object {
        private const val PERMISSION_REQUEST_CODE = 1001
        private val REQUIRED_PERMISSIONS = arrayOf(
            Manifest.permission.INTERNET,
            Manifest.permission.ACCESS_NETWORK_STATE,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.READ_EXTERNAL_STORAGE
        )
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // 初始化ViewModel
        viewModel = ViewModelProvider(this)[MainViewModel::class.java]
        
        // 设置工具栏
        setSupportActionBar(binding.toolbar)
        supportActionBar?.title = "闲鱼任务执行器"
        
        // 检查权限
        checkPermissions()
        
        // 设置UI
        setupUI()
        
        // 观察数据
        observeViewModel()
        
        Timber.d("MainActivity创建完成")
    }
    
    /**
     * 检查权限
     */
    private fun checkPermissions() {
        val missingPermissions = REQUIRED_PERMISSIONS.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        
        if (missingPermissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(
                this,
                missingPermissions.toTypedArray(),
                PERMISSION_REQUEST_CODE
            )
        } else {
            onPermissionsGranted()
        }
    }
    
    /**
     * 权限授予后的处理
     */
    private fun onPermissionsGranted() {
        // 启动后台服务
        startTaskExecutorService()
    }
    
    /**
     * 启动任务执行器服务
     */
    private fun startTaskExecutorService() {
        val intent = Intent(this, TaskExecutorService::class.java)
        ContextCompat.startForegroundService(this, intent)
        Timber.d("启动任务执行器服务")
    }
    
    /**
     * 设置UI
     */
    private fun setupUI() {
        // 连接按钮
        binding.btnConnect.setOnClickListener {
            val serverUrl = binding.etServerUrl.text.toString().trim()
            if (serverUrl.isNotEmpty()) {
                viewModel.connect(serverUrl)
            } else {
                Toast.makeText(this, "请输入服务器地址", Toast.LENGTH_SHORT).show()
            }
        }
        
        // 断开连接按钮
        binding.btnDisconnect.setOnClickListener {
            viewModel.disconnect()
        }
        
        // 清除日志按钮
        binding.btnClearLog.setOnClickListener {
            binding.tvLog.text = ""
        }
        
        // 设置按钮
        binding.btnSettings.setOnClickListener {
            // TODO: 打开设置页面
            Toast.makeText(this, "设置功能开发中", Toast.LENGTH_SHORT).show()
        }
        
        // 设置默认服务器地址
        binding.etServerUrl.setText("http://192.168.0.153:1888")
        
        // 设置设备信息
        val deviceId = Settings.Secure.getString(contentResolver, Settings.Secure.ANDROID_ID)
        val deviceName = "${android.os.Build.MANUFACTURER} ${android.os.Build.MODEL}"
        
        binding.tvDeviceId.text = "设备ID: $deviceId"
        binding.tvDeviceName.text = "设备名称: $deviceName"
        
        viewModel.setDeviceInfo(deviceId, deviceName)
    }
    
    /**
     * 观察ViewModel数据
     */
    private fun observeViewModel() {
        // 连接状态
        viewModel.connectionStatus.observe(this) { connected ->
            updateConnectionUI(connected)
        }
        
        // 任务状态
        viewModel.taskStatus.observe(this) { status ->
            binding.tvTaskStatus.text = "任务状态: $status"
        }
        
        // 日志消息
        viewModel.logMessages.observe(this) { messages ->
            binding.tvLog.text = messages.joinToString("\n")
            // 滚动到底部
            binding.scrollView.post {
                binding.scrollView.fullScroll(android.view.View.FOCUS_DOWN)
            }
        }
        
        // 统计信息
        viewModel.statistics.observe(this) { stats ->
            binding.tvCompletedTasks.text = "已完成任务: ${stats.completedTasks}"
            binding.tvFailedTasks.text = "失败任务: ${stats.failedTasks}"
            binding.tvTotalExecutionTime.text = "总执行时间: ${stats.totalExecutionTime}秒"
        }
        
        // 错误消息
        viewModel.errorMessage.observe(this) { message ->
            if (message.isNotEmpty()) {
                Toast.makeText(this, message, Toast.LENGTH_LONG).show()
            }
        }
    }
    
    /**
     * 更新连接状态UI
     */
    private fun updateConnectionUI(connected: Boolean) {
        if (connected) {
            binding.tvConnectionStatus.text = "连接状态: 已连接"
            binding.tvConnectionStatus.setTextColor(ContextCompat.getColor(this, R.color.green))
            binding.btnConnect.isEnabled = false
            binding.btnDisconnect.isEnabled = true
            binding.etServerUrl.isEnabled = false
        } else {
            binding.tvConnectionStatus.text = "连接状态: 未连接"
            binding.tvConnectionStatus.setTextColor(ContextCompat.getColor(this, R.color.red))
            binding.btnConnect.isEnabled = true
            binding.btnDisconnect.isEnabled = false
            binding.etServerUrl.isEnabled = true
        }
    }
    
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        
        if (requestCode == PERMISSION_REQUEST_CODE) {
            val allGranted = grantResults.all { it == PackageManager.PERMISSION_GRANTED }
            
            if (allGranted) {
                onPermissionsGranted()
            } else {
                Toast.makeText(this, "需要授予权限才能正常使用", Toast.LENGTH_LONG).show()
                finish()
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        Timber.d("MainActivity销毁")
    }
}
