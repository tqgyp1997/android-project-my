# 分布式任务系统 API 文档
*创建时间: 2025-09-17*

## 🌐 服务器信息
- **基础URL**: `http://localhost:1888`
- **WebSocket**: `ws://localhost:1888`
- **协议**: HTTP/WebSocket
- **数据格式**: JSON

## 📋 HTTP API 接口

### 1. 系统状态
```http
GET /
```

**响应示例:**
```json
{
  "system": "分布式任务系统",
  "version": "1.0.0",
  "status": "running",
  "port": 1888,
  "connected_devices": 2,
  "active_tasks": 5,
  "timestamp": "2025-09-17T14:30:00"
}
```

### 2. 设备管理

#### 获取设备列表
```http
GET /api/devices
```

**响应示例:**
```json
{
  "success": true,
  "devices": [
    {
      "device_id": "android_001",
      "device_name": "小米手机",
      "status": "online",
      "last_heartbeat": "2025-09-17T14:29:30",
      "task_count": 1,
      "connection_info": {
        "sid": "abc123",
        "registered_at": "2025-09-17T14:00:00"
      }
    }
  ],
  "total": 1
}
```

### 3. 任务管理

#### 获取任务列表
```http
GET /api/tasks
```

**响应示例:**
```json
{
  "success": true,
  "tasks": [
    {
      "task_id": "task_001",
      "task_type": "DELIST",
      "status": "running",
      "device_id": "android_001",
      "created_at": "2025-09-17T14:25:00",
      "data": {
        "product_ids": ["123", "456"],
        "action": "delist"
      }
    }
  ],
  "total": 1
}
```

#### 分发任务
```http
POST /api/dispatch-task
Content-Type: application/json

{
  "task_type": "DELIST",
  "data": {
    "product_ids": ["123", "456", "789"]
  },
  "device_id": "android_001"  // 可选
}
```

**响应示例:**
```json
{
  "success": true,
  "task_id": "task_002",
  "device_id": "android_001",
  "device_name": "小米手机",
  "message": "任务分发成功"
}
```

#### 获取任务状态
```http
GET /api/task/{task_id}/status
```

**响应示例:**
```json
{
  "success": true,
  "task": {
    "task_id": "task_001",
    "status": "completed",
    "progress": 100,
    "result": {
      "success": true,
      "processed_count": 3,
      "failed_count": 0,
      "message": "下架完成"
    },
    "updated_at": "2025-09-17T14:30:00"
  }
}
```

## 🔌 WebSocket 事件

### 客户端 → 服务器

#### 设备注册
```json
{
  "event": "device_register",
  "data": {
    "device_id": "android_001",
    "device_name": "小米手机",
    "device_info": {
      "type": "android",
      "version": "13",
      "app_version": "1.0.0"
    }
  }
}
```

#### 心跳
```json
{
  "event": "heartbeat",
  "data": {
    "device_id": "android_001",
    "timestamp": "2025-09-17T14:30:00"
  }
}
```

#### 任务结果
```json
{
  "event": "task_result",
  "data": {
    "task_id": "task_001",
    "result": {
      "success": true,
      "processed_count": 3,
      "failed_count": 0,
      "execution_time": 45.2,
      "message": "下架完成",
      "data": {
        "details": ["商品123已下架", "商品456已下架"]
      }
    }
  }
}
```

#### 任务进度
```json
{
  "event": "task_progress",
  "data": {
    "task_id": "task_001",
    "progress": 60,
    "message": "正在处理第2个商品..."
  }
}
```

### 服务器 → 客户端

#### 注册成功
```json
{
  "event": "register_success",
  "data": {
    "device_id": "android_001",
    "message": "注册成功",
    "server_time": "2025-09-17T14:30:00"
  }
}
```

#### 新任务
```json
{
  "event": "new_task",
  "data": {
    "type": "new_task",
    "task_id": "task_001",
    "task_type": "DELIST",
    "data": {
      "product_ids": ["123", "456"],
      "action": "delist"
    },
    "created_at": "2025-09-17T14:30:00",
    "timeout": 300
  }
}
```

#### 取消任务
```json
{
  "event": "cancel_task",
  "data": {
    "type": "cancel_task",
    "task_id": "task_001"
  }
}
```

#### 心跳确认
```json
{
  "event": "heartbeat_ack",
  "data": {
    "server_time": "2025-09-17T14:30:00"
  }
}
```

## 📱 任务类型定义

### DELIST - 下架任务
```json
{
  "task_type": "DELIST",
  "data": {
    "product_ids": ["123", "456", "789"],
    "batch_size": 10,
    "delay_between_items": 1.0,
    "retry_failed": true
  }
}
```

### COLLECT - 采集任务
```json
{
  "task_type": "COLLECT",
  "data": {
    "target_url": "https://example.com/shop",
    "max_items": 50,
    "scroll_delay": 2.0,
    "extract_images": true,
    "extract_details": true
  }
}
```

### UPLOAD - 上架任务
```json
{
  "task_type": "UPLOAD",
  "data": {
    "product_data": {
      "title": "商品标题",
      "price": 99.99,
      "description": "商品描述",
      "images": ["image1.jpg", "image2.jpg"]
    },
    "auto_publish": true,
    "schedule_time": null
  }
}
```

## 🔧 状态码说明

### 任务状态
- `pending`: 等待分发
- `dispatched`: 已分发到设备
- `running`: 正在执行
- `completed`: 执行完成
- `failed`: 执行失败
- `cancelled`: 已取消

### 设备状态
- `online`: 在线可用
- `offline`: 离线
- `busy`: 忙碌（任务已满）

## ⚠️ 错误处理

### HTTP 错误响应
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE"
}
```

### WebSocket 错误事件
```json
{
  "event": "error",
  "data": {
    "message": "错误描述",
    "error_code": "ERROR_CODE"
  }
}
```

## 🚀 快速开始示例

### 1. 启动服务器
```bash
cd distributed-task-system/server
python start_server.py
```

### 2. 设备连接（JavaScript示例）
```javascript
const socket = io('ws://localhost:1888');

// 注册设备
socket.emit('device_register', {
  device_id: 'android_001',
  device_name: '我的手机',
  device_info: {
    type: 'android',
    version: '13'
  }
});

// 监听新任务
socket.on('new_task', (data) => {
  console.log('收到新任务:', data);
  // 执行任务...
});
```

### 3. 分发任务（curl示例）
```bash
curl -X POST http://localhost:1888/api/dispatch-task \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "DELIST",
    "data": {
      "product_ids": ["123", "456"]
    }
  }'
```
