# 闲鱼任务执行器 Android APP
*创建时间: 2025-09-17*

## 📱 项目概述

这是闲鱼分布式任务系统的Android客户端，用于连接分布式任务服务器并执行各种任务（下架、采集、上架等）。

## 🏗️ 项目架构

### 技术栈
- **语言**: Kotlin
- **最低SDK**: Android 7.0 (API 24)
- **目标SDK**: Android 14 (API 34)
- **架构**: MVVM + Repository
- **网络**: OkHttp + Retrofit + Socket.IO
- **UI**: Material Design 3
- **异步**: Kotlin Coroutines

### 核心组件
```
app/
├── network/
│   └── WebSocketManager.kt          # WebSocket连接管理
├── task/
│   └── TaskExecutor.kt              # 任务执行器
├── service/
│   ├── TaskExecutorService.kt       # 后台服务
│   └── WebSocketService.kt          # WebSocket服务
├── ui/
│   └── MainActivity.kt              # 主界面
├── viewmodel/
│   └── MainViewModel.kt             # 主界面ViewModel
└── data/
    └── TaskRepository.kt            # 数据仓库
```

## 🚀 功能特性

### ✅ 已实现功能
1. **WebSocket连接** - 与分布式任务服务器实时通信
2. **设备注册** - 自动注册设备到服务器
3. **任务接收** - 接收服务器分发的任务
4. **下架任务** - 执行闲鱼商品下架操作
5. **进度上报** - 实时上报任务执行进度
6. **结果反馈** - 将任务结果发送回服务器
7. **后台运行** - 支持后台持续运行
8. **状态监控** - 实时显示连接和任务状态

### 🔄 开发中功能
1. **采集任务** - 商品信息采集
2. **上架任务** - 商品上架操作
3. **设置界面** - 详细配置选项
4. **任务历史** - 任务执行历史记录
5. **性能优化** - 内存和电量优化

## 📋 使用说明

### 安装要求
- Android 7.0 (API 24) 或更高版本
- 网络连接权限
- 存储权限（用于日志和缓存）

### 使用步骤
1. **安装APP** - 将APK安装到Android设备
2. **授予权限** - 允许网络和存储权限
3. **配置服务器** - 输入分布式任务服务器地址
4. **连接服务器** - 点击连接按钮建立连接
5. **等待任务** - APP将自动接收并执行任务

### 默认配置
- **服务器地址**: `http://192.168.0.153:1888`
- **设备ID**: 自动获取Android设备ID
- **设备名称**: 自动获取设备型号

## 🔧 开发环境

### 构建要求
- Android Studio Arctic Fox 或更高版本
- Kotlin 1.8+
- Gradle 8.0+
- JDK 8 或更高版本

### 构建步骤
```bash
# 1. 克隆项目
git clone <repository-url>

# 2. 打开Android Studio
# 选择 "Open an existing Android Studio project"
# 选择 android-app 目录

# 3. 同步项目
# Android Studio会自动下载依赖

# 4. 构建APK
./gradlew assembleDebug

# 5. 安装到设备
./gradlew installDebug
```

### 依赖库
```gradle
// 核心库
implementation 'androidx.core:core-ktx:1.12.0'
implementation 'androidx.appcompat:appcompat:1.6.1'
implementation 'com.google.android.material:material:1.11.0'

// 网络库
implementation 'io.socket:socket.io-client:2.0.1'
implementation 'com.squareup.okhttp3:okhttp:4.12.0'
implementation 'com.squareup.retrofit2:retrofit:2.9.0'

// WebView增强
implementation 'androidx.webkit:webkit:1.9.0'

// 协程
implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'

// 日志
implementation 'com.jakewharton.timber:timber:5.0.1'
```

## 🔌 API接口

### WebSocket事件

#### 客户端 → 服务器
```kotlin
// 设备注册
socket.emit("device_register", deviceInfo)

// 心跳
socket.emit("heartbeat", heartbeatData)

// 任务结果
socket.emit("task_result", resultData)

// 任务进度
socket.emit("task_progress", progressData)
```

#### 服务器 → 客户端
```kotlin
// 注册成功
socket.on("register_success") { data -> }

// 新任务
socket.on("new_task") { taskData -> }

// 取消任务
socket.on("cancel_task") { data -> }

// 心跳确认
socket.on("heartbeat_ack") { data -> }
```

### 任务数据格式

#### 下架任务
```json
{
  "task_id": "task_001",
  "task_type": "DELIST",
  "data": {
    "product_ids": ["123", "456", "789"],
    "batch_size": 10,
    "delay_between_items": 1.0,
    "retry_failed": true
  },
  "timeout": 300
}
```

#### 任务结果
```json
{
  "success": true,
  "message": "下架完成",
  "processed_count": 3,
  "failed_count": 0,
  "execution_time": 45.2,
  "data": {
    "processed_items": "123,456,789",
    "details": ["商品123已下架", "商品456已下架", "商品789已下架"]
  }
}
```

## 🐛 调试和日志

### 日志级别
- **VERBOSE**: 详细调试信息
- **DEBUG**: 调试信息
- **INFO**: 一般信息
- **WARN**: 警告信息
- **ERROR**: 错误信息

### 查看日志
```bash
# 查看应用日志
adb logcat | grep "XianyuTaskExecutor"

# 查看WebSocket日志
adb logcat | grep "WebSocketManager"

# 查看任务执行日志
adb logcat | grep "TaskExecutor"
```

## 📱 界面截图

### 主界面功能
1. **设备信息** - 显示设备ID和名称
2. **服务器连接** - 配置和管理服务器连接
3. **任务状态** - 显示当前任务状态和统计
4. **运行日志** - 实时显示运行日志

### 状态指示
- 🔴 **红色** - 未连接/错误状态
- 🟢 **绿色** - 已连接/成功状态
- 🟡 **黄色** - 连接中/处理中状态

## 🔒 权限说明

### 必需权限
- `INTERNET` - 网络连接
- `ACCESS_NETWORK_STATE` - 网络状态检测
- `FOREGROUND_SERVICE` - 后台服务运行
- `WAKE_LOCK` - 保持设备唤醒

### 可选权限
- `WRITE_EXTERNAL_STORAGE` - 日志文件存储
- `READ_EXTERNAL_STORAGE` - 读取配置文件

## 🚀 部署说明

### 测试部署
1. 使用Android Studio直接安装到测试设备
2. 确保测试设备与分布式服务器在同一网络
3. 配置正确的服务器IP地址

### 生产部署
1. 构建Release版本APK
2. 进行代码签名
3. 分发给目标设备
4. 配置生产服务器地址

## 🔧 故障排除

### 常见问题
1. **连接失败** - 检查服务器地址和网络连接
2. **权限被拒绝** - 确保授予所有必需权限
3. **任务执行失败** - 检查WebView和JavaScript执行环境
4. **后台被杀死** - 在设置中将APP加入白名单

### 性能优化
1. **内存优化** - 及时释放WebView资源
2. **电量优化** - 合理使用WakeLock
3. **网络优化** - 实现断线重连机制

## 📞 技术支持

### 开发团队
- **项目负责人**: 闲鱼开发团队
- **技术栈**: Android + Kotlin + WebSocket
- **创建时间**: 2025-09-17

### 相关文档
- [分布式任务系统文档](../README.md)
- [API接口文档](../docs/API.md)
- [集成指南](../integration/INTEGRATION_GUIDE.md)

---

*这个Android APP是闲鱼分布式任务系统的重要组成部分，为移动端任务执行提供了完整的解决方案！*
