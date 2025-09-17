#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务分发器 - 负责将任务分发给合适的设备
创建时间: 2025-09-17
"""

import logging
import json
from datetime import datetime
from typing import Dict, Optional
from models import Task, Device

logger = logging.getLogger(__name__)

class TaskDispatcher:
    """任务分发器"""
    
    def __init__(self, device_manager, socketio):
        """
        初始化任务分发器
        
        Args:
            device_manager: 设备管理器实例
            socketio: SocketIO实例
        """
        self.device_manager = device_manager
        self.socketio = socketio
        self.task_queue = []  # 待分发任务队列
        
    def dispatch_task(self, task: Task, target_device_id: str = None) -> Dict:
        """
        分发任务到设备
        
        Args:
            task: 任务对象
            target_device_id: 目标设备ID，为None时自动选择最优设备
            
        Returns:
            Dict: 分发结果
        """
        try:
            # 选择目标设备
            if target_device_id:
                target_device = self.device_manager.get_device(target_device_id)
                if not target_device:
                    return {
                        "success": False,
                        "message": f"指定设备不存在: {target_device_id}"
                    }
                if target_device.status != 'online':
                    return {
                        "success": False,
                        "message": f"指定设备不在线: {target_device_id}"
                    }
                if target_device.current_task_count >= target_device.max_concurrent_tasks:
                    return {
                        "success": False,
                        "message": f"指定设备任务已满: {target_device_id}"
                    }
            else:
                target_device = self.device_manager.get_best_device(task.task_type)
                if not target_device:
                    return {
                        "success": False,
                        "message": "没有可用设备"
                    }
            
            # 更新任务信息
            task.device_id = target_device.device_id
            task.status = 'dispatched'
            task.updated_at = datetime.now()
            
            # 增加设备任务计数
            self.device_manager.increment_task_count(target_device.device_id)
            
            # 发送任务到设备
            task_message = {
                "type": "new_task",
                "task_id": task.task_id,
                "task_type": task.task_type,
                "data": task.data,
                "created_at": task.created_at.isoformat(),
                "timeout": task.timeout
            }
            
            # 通过WebSocket发送任务
            self.socketio.emit('new_task', task_message, room=target_device.device_id)
            
            logger.info(f"📤 任务分发成功: {task.task_id} -> {target_device.name} ({target_device.device_id})")
            
            return {
                "success": True,
                "task_id": task.task_id,
                "device_id": target_device.device_id,
                "device_name": target_device.name,
                "message": "任务分发成功"
            }
            
        except Exception as e:
            logger.error(f"❌ 任务分发失败: {e}")
            return {
                "success": False,
                "message": f"任务分发失败: {str(e)}"
            }
    
    def create_delist_task(self, product_ids: list, device_id: str = None) -> Dict:
        """
        创建下架任务
        
        Args:
            product_ids: 商品ID列表
            device_id: 目标设备ID（可选）
            
        Returns:
            Dict: 创建结果
        """
        try:
            if not product_ids:
                return {
                    "success": False,
                    "message": "商品ID列表不能为空"
                }
            
            task_data = {
                "product_ids": product_ids,
                "batch_size": len(product_ids),
                "action": "delist"
            }
            
            task = Task(
                task_type="DELIST",
                data=task_data,
                timeout=300  # 5分钟超时
            )
            
            return self.dispatch_task(task, device_id)
            
        except Exception as e:
            logger.error(f"❌ 创建下架任务失败: {e}")
            return {
                "success": False,
                "message": f"创建下架任务失败: {str(e)}"
            }
    
    def create_collect_task(self, target_url: str, max_items: int = 50, device_id: str = None) -> Dict:
        """
        创建采集任务
        
        Args:
            target_url: 目标采集URL
            max_items: 最大采集数量
            device_id: 目标设备ID（可选）
            
        Returns:
            Dict: 创建结果
        """
        try:
            if not target_url:
                return {
                    "success": False,
                    "message": "目标URL不能为空"
                }
            
            task_data = {
                "target_url": target_url,
                "max_items": max_items,
                "action": "collect"
            }
            
            task = Task(
                task_type="COLLECT",
                data=task_data,
                timeout=600  # 10分钟超时
            )
            
            return self.dispatch_task(task, device_id)
            
        except Exception as e:
            logger.error(f"❌ 创建采集任务失败: {e}")
            return {
                "success": False,
                "message": f"创建采集任务失败: {str(e)}"
            }
    
    def create_upload_task(self, product_data: dict, device_id: str = None) -> Dict:
        """
        创建上架任务
        
        Args:
            product_data: 商品数据
            device_id: 目标设备ID（可选）
            
        Returns:
            Dict: 创建结果
        """
        try:
            if not product_data:
                return {
                    "success": False,
                    "message": "商品数据不能为空"
                }
            
            task_data = {
                "product_data": product_data,
                "action": "upload"
            }
            
            task = Task(
                task_type="UPLOAD",
                data=task_data,
                timeout=600  # 10分钟超时
            )
            
            return self.dispatch_task(task, device_id)
            
        except Exception as e:
            logger.error(f"❌ 创建上架任务失败: {e}")
            return {
                "success": False,
                "message": f"创建上架任务失败: {str(e)}"
            }
    
    def cancel_task(self, task_id: str) -> Dict:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 取消结果
        """
        try:
            # 这里需要从active_tasks中获取任务信息
            # 由于这个方法在app.py中调用，需要传入active_tasks
            # 暂时返回基本实现
            
            cancel_message = {
                "type": "cancel_task",
                "task_id": task_id
            }
            
            # 广播取消消息到所有设备
            self.socketio.emit('cancel_task', cancel_message)
            
            logger.info(f"🚫 任务取消请求已发送: {task_id}")
            
            return {
                "success": True,
                "message": "任务取消请求已发送"
            }
            
        except Exception as e:
            logger.error(f"❌ 取消任务失败: {e}")
            return {
                "success": False,
                "message": f"取消任务失败: {str(e)}"
            }
    
    def get_task_queue_status(self) -> Dict:
        """
        获取任务队列状态
        
        Returns:
            Dict: 队列状态信息
        """
        try:
            return {
                "queue_length": len(self.task_queue),
                "available_devices": len(self.device_manager.get_available_devices()),
                "online_devices": len(self.device_manager.get_online_devices()),
                "total_devices": len(self.device_manager.get_all_devices())
            }
            
        except Exception as e:
            logger.error(f"❌ 获取队列状态失败: {e}")
            return {}
    
    def broadcast_message(self, message: dict, device_ids: list = None) -> bool:
        """
        广播消息到设备
        
        Args:
            message: 要广播的消息
            device_ids: 目标设备ID列表，为None时广播到所有在线设备
            
        Returns:
            bool: 广播是否成功
        """
        try:
            if device_ids:
                # 发送到指定设备
                for device_id in device_ids:
                    self.socketio.emit('broadcast', message, room=device_id)
            else:
                # 广播到所有在线设备
                online_devices = self.device_manager.get_online_devices()
                for device in online_devices:
                    self.socketio.emit('broadcast', message, room=device.device_id)
            
            logger.info(f"📢 消息广播完成: {len(device_ids) if device_ids else len(online_devices)}个设备")
            return True
            
        except Exception as e:
            logger.error(f"❌ 广播消息失败: {e}")
            return False
    
    def get_device_load_balance_info(self) -> Dict:
        """
        获取设备负载均衡信息
        
        Returns:
            Dict: 负载均衡信息
        """
        try:
            devices = self.device_manager.get_all_devices()
            device_info = []
            
            for device in devices:
                load_percentage = (device.current_task_count / device.max_concurrent_tasks) * 100
                device_info.append({
                    "device_id": device.device_id,
                    "device_name": device.name,
                    "status": device.status,
                    "current_tasks": device.current_task_count,
                    "max_tasks": device.max_concurrent_tasks,
                    "load_percentage": round(load_percentage, 2)
                })
            
            # 按负载排序
            device_info.sort(key=lambda x: x["load_percentage"])
            
            return {
                "devices": device_info,
                "total_devices": len(devices),
                "average_load": sum(d["load_percentage"] for d in device_info) / max(1, len(device_info))
            }
            
        except Exception as e:
            logger.error(f"❌ 获取负载均衡信息失败: {e}")
            return {}
