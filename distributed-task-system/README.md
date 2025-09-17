# 分布式任务系统 - 闲鱼下架专用
*创建时间: 2025-09-17*

## 🎯 项目目标
解决现有系统的Playwright线程冲突问题，通过分布式架构实现：
- 后台系统下发任务
- 手机APP接受并执行任务  
- 实时反馈执行结果
- 多设备并行处理

## 🏗️ 系统架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   管理后台       │    │   任务调度服务   │    │   手机APP集群    │
│  (现有系统)      │◄──►│  (新增独立)     │◄──►│  (新开发)       │
│                 │    │                 │    │                 │
│ • 任务创建       │    │ • 任务分发       │    │ • 任务执行       │
│ • 结果查看       │    │ • 设备管理       │    │ • 状态上报       │
│ • 设备监控       │    │ • 实时通信       │    │ • 自动重试       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 目录结构
```
distributed-task-system/
├── server/                 # 任务调度服务端
│   ├── app.py             # Flask主应用
│   ├── device_manager.py  # 设备管理
│   ├── task_dispatcher.py # 任务分发器
│   ├── websocket_handler.py # WebSocket处理
│   └── models.py          # 数据模型
├── android-app/           # Android客户端
│   ├── app/               # 应用源码
│   └── build.gradle       # 构建配置
├── docs/                  # 文档
└── README.md              # 项目说明
```

## 🚀 快速开始

### 服务端启动
```bash
cd distributed-task-system/server
pip install -r requirements.txt
python app.py
```

### 客户端安装
1. 使用Android Studio打开android-app项目
2. 修改服务器地址配置
3. 编译安装到手机

## 🔧 核心功能

### 任务类型
- **DELIST**: 商品下架任务
- **COLLECT**: 商品信息采集
- **UPLOAD**: 商品上架任务

### 通信协议
- **WebSocket**: 实时双向通信
- **HTTP API**: RESTful接口
- **JSON**: 数据交换格式

## 📊 技术栈

### 服务端
- **Python 3.x**: 主要语言
- **Flask**: Web框架
- **Flask-SocketIO**: WebSocket支持
- **SQLite**: 轻量数据库
- **Redis**: 任务队列(可选)

### 客户端
- **Android原生**: Kotlin/Java
- **OkHttp**: 网络请求
- **WebSocket**: 实时通信
- **Room**: 本地数据库(可选)

## ⚠️ 开发规范
- 端口使用: 1888 (避免与现有1887冲突)
- 测试代码标记: `// TEST: 临时测试-日期`
- 代码提交前清理测试代码
- 遵循 `.augment-guidelines` 规范

## 🔄 开发计划
- [x] 项目结构创建
- [ ] 服务端核心功能
- [ ] WebSocket通信
- [ ] Android APP开发
- [ ] 端到端测试
- [ ] 部署优化

## 📝 API文档
详见 `docs/API.md`

## 🎉 预期效果
- ✅ 彻底解决线程冲突问题
- ✅ 支持多设备并行执行
- ✅ 实时监控任务状态
- ✅ 自动故障恢复
- ✅ 易于扩展和维护
