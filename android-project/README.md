# 闲鱼任务执行器 - Android应用

## 📱 项目说明
这是一个简单的Android应用，用于连接闲鱼管理系统。

## 🔧 技术规格
- **端口**: 固定1887（不可修改）
- **管理端地址**: http://localhost:1887/admin#
- **最低Android版本**: 7.0 (API 24)
- **目标Android版本**: 14 (API 34)

## 🚀 构建说明
1. 使用Android Studio打开项目
2. 等待Gradle同步完成
3. 点击"Build" → "Build Bundle(s) / APK(s)" → "Build APK(s)"
4. APK文件将生成在 `app/build/outputs/apk/debug/` 目录

## 📋 功能特性
- 连接到本地闲鱼管理系统
- 显示连接状态
- 简单的用户界面

## ⚠️ 重要说明
- 端口1887是固定的，不要修改
- 确保闲鱼管理系统在端口1887上运行
- 应用需要网络权限才能正常工作
