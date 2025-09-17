package com.xianyu.taskexecutor;

import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.Button;
import android.view.View;
import android.util.Log;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.Call;
import okhttp3.Callback;

import java.io.IOException;

public class MainActivity extends AppCompatActivity {
    
    // 端口固定为1887，不可修改，对应管理端地址：http://localhost:1887/admin#
    private static final String ADMIN_URL = "http://localhost:1887/admin#";
    private static final int ADMIN_PORT = 1887;
    
    private TextView statusText;
    private Button connectButton;
    private OkHttpClient client;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        statusText = findViewById(R.id.statusText);
        connectButton = findViewById(R.id.connectButton);
        client = new OkHttpClient();
        
        connectButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                connectToServer();
            }
        });
        
        statusText.setText("闲鱼任务执行器已启动\n管理端地址: " + ADMIN_URL);
    }
    
    private void connectToServer() {
        String url = "http://localhost:" + ADMIN_PORT + "/api/status";
        Request request = new Request.Builder()
                .url(url)
                .build();
                
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                runOnUiThread(() -> {
                    statusText.setText("连接失败: " + e.getMessage());
                });
            }
            
            @Override
            public void onResponse(Call call, Response response) throws IOException {
                runOnUiThread(() -> {
                    if (response.isSuccessful()) {
                        statusText.setText("连接成功！\n服务器状态: 正常");
                    } else {
                        statusText.setText("连接失败，状态码: " + response.code());
                    }
                });
            }
        });
    }
}
