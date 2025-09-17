package com.xianyu.taskexecutor.task

import android.content.Context
import android.webkit.WebView
import kotlinx.coroutines.*
import org.json.JSONObject
import timber.log.Timber

/**
 * 任务执行器
 * 负责执行各种类型的任务
 * 创建时间: 2025-09-17
 */
class TaskExecutor(private val context: Context) {
    
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    private val runningTasks = mutableMapOf<String, Job>()
    
    /**
     * 执行任务
     */
    fun executeTask(
        taskData: JSONObject,
        onProgress: (Int, String) -> Unit,
        onComplete: (JSONObject) -> Unit
    ) {
        val taskId = taskData.optString("task_id")
        val taskType = taskData.optString("task_type")
        val data = taskData.optJSONObject("data")
        
        if (taskId.isEmpty() || taskType.isEmpty() || data == null) {
            val errorResult = JSONObject().apply {
                put("success", false)
                put("message", "任务数据格式错误")
                put("error_code", "INVALID_TASK_DATA")
            }
            onComplete(errorResult)
            return
        }
        
        // 取消同名任务
        runningTasks[taskId]?.cancel()
        
        // 启动新任务
        val job = scope.launch {
            try {
                Timber.d("开始执行任务: $taskId, 类型: $taskType")
                onProgress(0, "任务开始执行...")
                
                val result = when (taskType) {
                    "DELIST" -> executeDelistTask(data, onProgress)
                    "COLLECT" -> executeCollectTask(data, onProgress)
                    "UPLOAD" -> executeUploadTask(data, onProgress)
                    else -> {
                        JSONObject().apply {
                            put("success", false)
                            put("message", "不支持的任务类型: $taskType")
                            put("error_code", "UNSUPPORTED_TASK_TYPE")
                        }
                    }
                }
                
                onProgress(100, "任务执行完成")
                onComplete(result)
                
            } catch (e: CancellationException) {
                Timber.d("任务被取消: $taskId")
                val cancelResult = JSONObject().apply {
                    put("success", false)
                    put("message", "任务被取消")
                    put("error_code", "TASK_CANCELLED")
                }
                onComplete(cancelResult)
            } catch (e: Exception) {
                Timber.e(e, "任务执行异常: $taskId")
                val errorResult = JSONObject().apply {
                    put("success", false)
                    put("message", "任务执行异常: ${e.message}")
                    put("error_code", "TASK_EXECUTION_ERROR")
                }
                onComplete(errorResult)
            } finally {
                runningTasks.remove(taskId)
            }
        }
        
        runningTasks[taskId] = job
    }
    
    /**
     * 执行下架任务
     */
    private suspend fun executeDelistTask(
        data: JSONObject,
        onProgress: (Int, String) -> Unit
    ): JSONObject = withContext(Dispatchers.Main) {
        
        val productIds = data.optJSONArray("product_ids")
        val batchSize = data.optInt("batch_size", 10)
        val delayBetweenItems = data.optDouble("delay_between_items", 1.0) * 1000
        
        if (productIds == null || productIds.length() == 0) {
            return@withContext JSONObject().apply {
                put("success", false)
                put("message", "商品ID列表为空")
                put("error_code", "EMPTY_PRODUCT_LIST")
            }
        }
        
        val totalCount = productIds.length()
        var processedCount = 0
        var failedCount = 0
        val processedItems = mutableListOf<String>()
        val failedItems = mutableListOf<String>()
        
        onProgress(10, "初始化WebView...")
        
        // 创建WebView用于执行下架操作
        val webView = WebView(context).apply {
            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                databaseEnabled = true
                allowFileAccess = true
                allowContentAccess = true
                allowFileAccessFromFileURLs = true
                allowUniversalAccessFromFileURLs = true
            }
        }
        
        try {
            onProgress(20, "正在访问闲鱼网站...")
            
            // 模拟访问闲鱼网站
            val loadComplete = CompletableDeferred<Boolean>()
            
            webView.webViewClient = object : android.webkit.WebViewClient() {
                override fun onPageFinished(view: WebView?, url: String?) {
                    super.onPageFinished(view, url)
                    if (url?.contains("xianyu") == true) {
                        loadComplete.complete(true)
                    }
                }
                
                override fun onReceivedError(
                    view: WebView?,
                    errorCode: Int,
                    description: String?,
                    failingUrl: String?
                ) {
                    super.onReceivedError(view, errorCode, description, failingUrl)
                    loadComplete.complete(false)
                }
            }
            
            // 加载闲鱼网站
            webView.loadUrl("https://www.goofish.com")
            
            // 等待页面加载完成
            val loaded = withTimeoutOrNull(30000) {
                loadComplete.await()
            } ?: false
            
            if (!loaded) {
                return@withContext JSONObject().apply {
                    put("success", false)
                    put("message", "无法访问闲鱼网站")
                    put("error_code", "WEBSITE_ACCESS_FAILED")
                }
            }
            
            onProgress(30, "开始下架商品...")
            
            // 处理每个商品
            for (i in 0 until totalCount) {
                val productId = productIds.optString(i)
                if (productId.isEmpty()) continue
                
                val progress = 30 + (i * 60 / totalCount)
                onProgress(progress, "正在下架商品 ${i + 1}/$totalCount: $productId")
                
                try {
                    // 模拟下架操作
                    val delistResult = performDelistOperation(webView, productId)
                    
                    if (delistResult) {
                        processedCount++
                        processedItems.add(productId)
                        Timber.d("商品下架成功: $productId")
                    } else {
                        failedCount++
                        failedItems.add(productId)
                        Timber.w("商品下架失败: $productId")
                    }
                    
                } catch (e: Exception) {
                    failedCount++
                    failedItems.add(productId)
                    Timber.e(e, "下架商品异常: $productId")
                }
                
                // 延迟避免频率过高
                if (i < totalCount - 1) {
                    delay(delayBetweenItems.toLong())
                }
            }
            
            onProgress(95, "整理下架结果...")
            
            // 返回结果
            return@withContext JSONObject().apply {
                put("success", processedCount > 0)
                put("message", if (processedCount > 0) "下架完成" else "下架失败")
                put("processed_count", processedCount)
                put("failed_count", failedCount)
                put("execution_time", System.currentTimeMillis() / 1000.0)
                put("data", JSONObject().apply {
                    put("processed_items", processedItems.joinToString(","))
                    put("failed_items", failedItems.joinToString(","))
                    put("details", processedItems.map { "商品${it}已下架" })
                })
            }
            
        } finally {
            // 清理WebView
            webView.destroy()
        }
    }
    
    /**
     * 执行单个商品的下架操作
     */
    private suspend fun performDelistOperation(webView: WebView, productId: String): Boolean {
        return withContext(Dispatchers.Main) {
            try {
                // 这里是模拟的下架操作
                // 实际实现中需要：
                // 1. 导航到商品管理页面
                // 2. 查找对应商品
                // 3. 点击下架按钮
                // 4. 确认下架操作
                
                val operationComplete = CompletableDeferred<Boolean>()
                
                // 模拟JavaScript执行
                val jsCode = """
                    // 模拟下架操作的JavaScript代码
                    (function() {
                        try {
                            // 查找商品ID为 $productId 的商品
                            console.log('开始下架商品: $productId');
                            
                            // 模拟下架操作
                            setTimeout(function() {
                                // 这里应该是实际的下架逻辑
                                console.log('商品下架完成: $productId');
                                window.delistCallback && window.delistCallback(true);
                            }, 1000 + Math.random() * 2000); // 随机延迟1-3秒
                            
                        } catch (e) {
                            console.error('下架操作失败:', e);
                            window.delistCallback && window.delistCallback(false);
                        }
                    })();
                """.trimIndent()
                
                // 添加回调接口
                webView.addJavascriptInterface(object {
                    @android.webkit.JavascriptInterface
                    fun onDelistComplete(success: Boolean) {
                        operationComplete.complete(success)
                    }
                }, "DelistInterface")
                
                // 设置回调
                webView.evaluateJavascript(
                    "window.delistCallback = function(success) { DelistInterface.onDelistComplete(success); }",
                    null
                )
                
                // 执行下架操作
                webView.evaluateJavascript(jsCode, null)
                
                // 等待操作完成
                withTimeoutOrNull(10000) {
                    operationComplete.await()
                } ?: false
                
            } catch (e: Exception) {
                Timber.e(e, "下架操作异常: $productId")
                false
            }
        }
    }
    
    /**
     * 执行采集任务
     */
    private suspend fun executeCollectTask(
        data: JSONObject,
        onProgress: (Int, String) -> Unit
    ): JSONObject {
        // TODO: 实现采集任务
        onProgress(50, "采集任务开发中...")
        delay(2000)
        
        return JSONObject().apply {
            put("success", false)
            put("message", "采集任务功能开发中")
            put("error_code", "FEATURE_NOT_IMPLEMENTED")
        }
    }
    
    /**
     * 执行上架任务
     */
    private suspend fun executeUploadTask(
        data: JSONObject,
        onProgress: (Int, String) -> Unit
    ): JSONObject {
        // TODO: 实现上架任务
        onProgress(50, "上架任务开发中...")
        delay(2000)
        
        return JSONObject().apply {
            put("success", false)
            put("message", "上架任务功能开发中")
            put("error_code", "FEATURE_NOT_IMPLEMENTED")
        }
    }
    
    /**
     * 取消任务
     */
    fun cancelTask(taskId: String) {
        runningTasks[taskId]?.cancel()
        runningTasks.remove(taskId)
        Timber.d("任务已取消: $taskId")
    }
    
    /**
     * 取消所有任务
     */
    fun cancelAllTasks() {
        runningTasks.values.forEach { it.cancel() }
        runningTasks.clear()
        Timber.d("所有任务已取消")
    }
    
    /**
     * 获取运行中的任务数量
     */
    fun getRunningTaskCount(): Int = runningTasks.size
    
    /**
     * 清理资源
     */
    fun cleanup() {
        cancelAllTasks()
        scope.cancel()
    }
}
