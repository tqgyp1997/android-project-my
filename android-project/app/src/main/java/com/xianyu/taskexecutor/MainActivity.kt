package com.xianyu.taskexecutor

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import okhttp3.*
import java.io.IOException

class MainActivity : AppCompatActivity() {
    
    // 端口固定为1887，不可修改，对应管理端地址：http://localhost:1887/admin#
    private companion object {
        const val ADMIN_URL = "http://localhost:1887/admin#"
        const val ADMIN_PORT = 1887
        const val TEST_URL = "http://localhost:1887/api/health"
    }
    
    private lateinit var statusText: TextView
    private lateinit var connectButton: Button
    private val client = OkHttpClient()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        statusText = findViewById(R.id.statusText)
        connectButton = findViewById(R.id.connectButton)
        
        connectButton.setOnClickListener {
            testConnection()
        }
        
        statusText.text = "闲鱼任务执行器\n管理端地址: $ADMIN_URL\n点击测试连接"
    }
    
    private fun testConnection() {
        statusText.text = "正在连接管理端..."
        connectButton.isEnabled = false
        
        val request = Request.Builder()
            .url(TEST_URL)
            .build()
            
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    statusText.text = "连接失败: ${e.message}\n请确保管理端正在运行\n地址: $ADMIN_URL"
                    connectButton.isEnabled = true
                }
            }
            
            override fun onResponse(call: Call, response: Response) {
                runOnUiThread {
                    if (response.isSuccessful) {
                        statusText.text = "连接成功！\n管理端地址: $ADMIN_URL\n状态: 正常运行"
                    } else {
                        statusText.text = "连接失败\n状态码: ${response.code}\n地址: $ADMIN_URL"
                    }
                    connectButton.isEnabled = true
                }
            }
        })
    }
}
