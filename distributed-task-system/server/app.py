#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分布式任务系统 - 主服务器
创建时间: 2025-09-17
端口: 1888 (独立于现有系统的1887端口)
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional
import threading
import time

# 导入自定义模块
from device_manager import DeviceManager
from task_dispatcher import TaskDispatcher
from models import Task, Device, TaskResult

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'distributed-task-system-2025'

# 启用CORS和SocketIO
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# 初始化核心组件
device_manager = DeviceManager()
task_dispatcher = TaskDispatcher(device_manager, socketio)

# 全局变量
connected_devices: Dict[str, Dict] = {}  # device_id -> connection_info
active_tasks: Dict[str, Task] = {}  # task_id -> task

# ==================== HTTP API 接口 ====================

@app.route('/', methods=['GET'])
def index():
    """系统状态页面"""
    return jsonify({
        "system": "分布式任务系统",
        "version": "1.0.0",
        "status": "running",
        "port": 1888,
        "connected_devices": len(connected_devices),
        "active_tasks": len(active_tasks),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """获取所有设备列表"""
    devices = []
    for device_id, device_info in connected_devices.items():
        device = device_manager.get_device(device_id)
        if device:
            devices.append({
                "device_id": device_id,
                "device_name": device.name,
                "status": device.status,
                "last_heartbeat": device.last_heartbeat.isoformat() if device.last_heartbeat else None,
                "task_count": device.current_task_count,
                "connection_info": device_info
            })
    
    return jsonify({
        "success": True,
        "devices": devices,
        "total": len(devices)
    })

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取所有任务列表"""
    tasks = []
    for task_id, task in active_tasks.items():
        tasks.append({
            "task_id": task_id,
            "task_type": task.task_type,
            "status": task.status,
            "device_id": task.device_id,
            "created_at": task.created_at.isoformat(),
            "data": task.data
        })
    
    return jsonify({
        "success": True,
        "tasks": tasks,
        "total": len(tasks)
    })

@app.route('/api/dispatch-task', methods=['POST'])
def dispatch_task():
    """分发任务到设备"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        if not data or 'task_type' not in data:
            return jsonify({
                "success": False,
                "message": "缺少必要参数: task_type"
            }), 400
        
        task_type = data['task_type']
        task_data = data.get('data', {})
        device_id = data.get('device_id')  # 可选，不指定则自动选择
        
        # 创建任务
        task = Task(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            data=task_data,
            status='pending',
            created_at=datetime.now()
        )
        
        # 分发任务
        result = task_dispatcher.dispatch_task(task, device_id)
        
        if result['success']:
            active_tasks[task.task_id] = task
            logger.info(f"✅ 任务分发成功: {task.task_id} -> {result.get('device_id')}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ 分发任务失败: {e}")
        return jsonify({
            "success": False,
            "message": f"分发任务失败: {str(e)}"
        }), 500

@app.route('/api/task/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    if task_id in active_tasks:
        task = active_tasks[task_id]
        return jsonify({
            "success": True,
            "task": {
                "task_id": task_id,
                "status": task.status,
                "progress": task.progress,
                "result": task.result,
                "error": task.error,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            }
        })
    else:
        return jsonify({
            "success": False,
            "message": "任务不存在"
        }), 404

# ==================== WebSocket 事件处理 ====================

@socketio.on('connect')
def handle_connect():
    """客户端连接事件"""
    logger.info(f"🔗 新的连接: {request.sid}")
    emit('connected', {'message': '连接成功', 'sid': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接事件"""
    logger.info(f"🔌 连接断开: {request.sid}")
    
    # 查找并移除断开的设备
    device_to_remove = None
    for device_id, device_info in connected_devices.items():
        if device_info.get('sid') == request.sid:
            device_to_remove = device_id
            break
    
    if device_to_remove:
        device_manager.update_device_status(device_to_remove, 'offline')
        connected_devices.pop(device_to_remove, None)
        logger.info(f"📱 设备离线: {device_to_remove}")

@socketio.on('device_register')
def handle_device_register(data):
    """设备注册事件"""
    try:
        device_id = data.get('device_id')
        device_name = data.get('device_name', f'设备_{device_id[:8]}')
        device_info = data.get('device_info', {})
        
        if not device_id:
            emit('register_error', {'message': '设备ID不能为空'})
            return
        
        # 创建设备对象
        device = Device(
            device_id=device_id,
            name=device_name,
            device_type=device_info.get('type', 'android'),
            status='online',
            last_heartbeat=datetime.now(),
            registered_at=datetime.now()
        )
        
        # 注册设备
        device_manager.register_device(device)
        
        # 保存连接信息
        connected_devices[device_id] = {
            'sid': request.sid,
            'device_name': device_name,
            'registered_at': datetime.now().isoformat(),
            'device_info': device_info
        }
        
        # 加入设备房间
        join_room(device_id)
        
        logger.info(f"📱 设备注册成功: {device_name} ({device_id})")
        emit('register_success', {
            'device_id': device_id,
            'message': '注册成功',
            'server_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ 设备注册失败: {e}")
        emit('register_error', {'message': f'注册失败: {str(e)}'})

@socketio.on('heartbeat')
def handle_heartbeat(data):
    """心跳事件"""
    device_id = data.get('device_id')
    if device_id and device_id in connected_devices:
        device_manager.update_device_status(device_id, 'online')
        emit('heartbeat_ack', {'server_time': datetime.now().isoformat()})

@socketio.on('task_result')
def handle_task_result(data):
    """任务结果事件"""
    try:
        task_id = data.get('task_id')
        result_data = data.get('result', {})
        
        if task_id in active_tasks:
            task = active_tasks[task_id]
            task.status = 'completed' if result_data.get('success') else 'failed'
            task.result = result_data
            task.updated_at = datetime.now()
            
            # 更新设备任务计数
            if task.device_id:
                device = device_manager.get_device(task.device_id)
                if device:
                    device.current_task_count = max(0, device.current_task_count - 1)
            
            logger.info(f"📋 任务完成: {task_id} - {task.status}")
            emit('task_result_ack', {'task_id': task_id, 'status': 'received'})
        else:
            logger.warning(f"⚠️ 收到未知任务结果: {task_id}")
            
    except Exception as e:
        logger.error(f"❌ 处理任务结果失败: {e}")

@socketio.on('task_progress')
def handle_task_progress(data):
    """任务进度更新事件"""
    task_id = data.get('task_id')
    progress = data.get('progress', 0)
    
    if task_id in active_tasks:
        active_tasks[task_id].progress = progress
        active_tasks[task_id].updated_at = datetime.now()
        logger.debug(f"📊 任务进度更新: {task_id} - {progress}%")

# ==================== 启动服务器 ====================

def start_cleanup_thread():
    """启动清理线程，定期清理过期任务和离线设备"""
    def cleanup_worker():
        while True:
            try:
                # 清理完成的任务（保留1小时）
                current_time = datetime.now()
                expired_tasks = []
                
                for task_id, task in active_tasks.items():
                    if task.status in ['completed', 'failed']:
                        time_diff = (current_time - task.updated_at).total_seconds()
                        if time_diff > 3600:  # 1小时
                            expired_tasks.append(task_id)
                
                for task_id in expired_tasks:
                    active_tasks.pop(task_id, None)
                    logger.info(f"🗑️ 清理过期任务: {task_id}")
                
                # 检查设备心跳
                device_manager.check_device_heartbeat()
                
                time.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                logger.error(f"❌ 清理线程异常: {e}")
                time.sleep(60)
    
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()
    logger.info("🧹 清理线程已启动")

if __name__ == '__main__':
    logger.info("🚀 启动分布式任务系统服务器...")
    logger.info("📡 端口: 1888")
    logger.info("🌐 管理地址: http://localhost:1888")
    
    # 启动清理线程
    start_cleanup_thread()
    
    # 启动服务器
    socketio.run(app, host='0.0.0.0', port=1888, debug=False)
