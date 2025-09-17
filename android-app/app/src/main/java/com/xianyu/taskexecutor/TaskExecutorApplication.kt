package com.xianyu.taskexecutor

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import timber.log.Timber

/**
 * 闲鱼任务执行器应用程序类
 * 创建时间: 2025-09-17
 */
class TaskExecutorApplication : Application() {
    
    companion object {
        const val NOTIFICATION_CHANNEL_ID = "task_executor_channel"
        const val NOTIFICATION_CHANNEL_NAME = "任务执行器"
        
        lateinit var instance: TaskExecutorApplication
            private set
    }
    
    override fun onCreate() {
        super.onCreate()
        instance = this
        
        // 初始化日志
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }
        
        // 创建通知渠道
        createNotificationChannel()
        
        Timber.d("闲鱼任务执行器应用启动")
    }
    
    /**
     * 创建通知渠道（Android 8.0+）
     */
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                NOTIFICATION_CHANNEL_ID,
                NOTIFICATION_CHANNEL_NAME,
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "闲鱼任务执行器后台服务通知"
                setShowBadge(false)
            }
            
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }
}
