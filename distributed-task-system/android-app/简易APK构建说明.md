# 📱 闲鱼任务执行器 Android APP 安装指南

## 🎯 当前状态

✅ **Android APP代码已完成**
- 完整的Kotlin源代码
- WebSocket连接管理
- 任务执行器
- Material Design界面

⚠️ **需要构建APK文件**
- 源代码已就绪，需要编译成APK
- 需要Android开发环境

## 📋 安装方法

### 方法一：使用Android Studio（推荐）

1. **安装Android Studio**
   - 下载：https://developer.android.com/studio
   - 安装Android SDK和相关工具

2. **打开项目**
   ```
   1. 启动Android Studio
   2. 选择 "Open an existing Android Studio project"
   3. 选择目录：distributed-task-system/android-app
   4. 等待项目同步完成
   ```

3. **构建APK**
   ```
   1. 在Android Studio中点击 Build → Build Bundle(s) / APK(s) → Build APK(s)
   2. 等待构建完成
   3. APK文件位置：app/build/outputs/apk/debug/app-debug.apk
   ```

4. **安装到手机**
   ```
   1. 连接Android手机到电脑
   2. 启用USB调试模式
   3. 运行：adb install app-debug.apk
   或者直接将APK文件传输到手机安装
   ```

### 方法二：命令行构建

1. **环境要求**
   - Java JDK 8+
   - Android SDK
   - 设置ANDROID_HOME环境变量

2. **构建命令**
   ```bash
   cd distributed-task-system/android-app
   ./gradlew assembleDebug
   ```

3. **安装命令**
   ```bash
   ./gradlew installDebug
   ```

### 方法三：在线构建服务（简单）

如果您不想安装Android Studio，我可以帮您：

1. **打包源代码**
   - 将android-app目录打包
   - 上传到在线Android构建服务

2. **推荐服务**
   - GitHub Actions（免费）
   - AppCenter（微软）
   - CircleCI

## 🔧 手动安装步骤

如果您有现成的APK文件：

1. **启用未知来源**
   ```
   设置 → 安全 → 未知来源 → 开启
   ```

2. **安装APK**
   ```
   1. 将APK文件传输到手机
   2. 点击APK文件
   3. 按提示安装
   ```

3. **授予权限**
   ```
   - 网络权限
   - 存储权限
   - 前台服务权限
   ```

## 📱 APP使用说明

1. **首次启动**
   - 打开"闲鱼任务执行器"
   - 授予必要权限

2. **配置服务器**
   - 服务器地址：http://您的电脑IP:1888
   - 例如：http://192.168.1.100:1888

3. **连接测试**
   - 点击"连接"按钮
   - 查看连接状态
   - 等待任务分发

## 🚀 快速解决方案

**如果您希望立即测试**，我建议：

1. **我帮您构建APK**
   - 我可以创建一个简化版本
   - 生成可直接安装的APK文件

2. **使用现有工具**
   - 先启动分布式任务系统服务器
   - 通过Web界面测试功能
   - 后续再添加移动端

您希望我现在：
- ✅ 帮您构建一个简化的APK文件？
- ✅ 先启动分布式任务系统服务器进行测试？
- ✅ 创建Web版的移动端界面作为替代？

请告诉我您的偏好！
