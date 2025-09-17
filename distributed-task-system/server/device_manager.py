#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备管理器 - 管理所有连接的设备
创建时间: 2025-09-17
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from models import Device

logger = logging.getLogger(__name__)

class DeviceManager:
    """设备管理器"""
    
    def __init__(self):
        self.devices: Dict[str, Device] = {}  # device_id -> Device
        self.device_status: Dict[str, str] = {}  # device_id -> status
        self.heartbeat_timeout = 300  # 5分钟心跳超时
        
    def register_device(self, device: Device) -> bool:
        """
        注册新设备
        
        Args:
            device: 设备对象
            
        Returns:
            bool: 注册是否成功
        """
        try:
            device_id = device.device_id
            
            # 如果设备已存在，更新信息
            if device_id in self.devices:
                existing_device = self.devices[device_id]
                existing_device.name = device.name
                existing_device.device_type = device.device_type
                existing_device.status = 'online'
                existing_device.last_heartbeat = datetime.now()
                logger.info(f"📱 设备重新连接: {device.name} ({device_id})")
            else:
                # 新设备注册
                self.devices[device_id] = device
                logger.info(f"📱 新设备注册: {device.name} ({device_id})")
            
            self.device_status[device_id] = 'online'
            return True
            
        except Exception as e:
            logger.error(f"❌ 设备注册失败: {e}")
            return False
    
    def unregister_device(self, device_id: str) -> bool:
        """
        注销设备
        
        Args:
            device_id: 设备ID
            
        Returns:
            bool: 注销是否成功
        """
        try:
            if device_id in self.devices:
                device = self.devices[device_id]
                device.status = 'offline'
                self.device_status[device_id] = 'offline'
                logger.info(f"📱 设备注销: {device.name} ({device_id})")
                return True
            else:
                logger.warning(f"⚠️ 尝试注销不存在的设备: {device_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 设备注销失败: {e}")
            return False
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """
        获取设备信息
        
        Args:
            device_id: 设备ID
            
        Returns:
            Device: 设备对象，不存在则返回None
        """
        return self.devices.get(device_id)
    
    def get_all_devices(self) -> List[Device]:
        """
        获取所有设备列表
        
        Returns:
            List[Device]: 设备列表
        """
        return list(self.devices.values())
    
    def get_online_devices(self) -> List[Device]:
        """
        获取所有在线设备
        
        Returns:
            List[Device]: 在线设备列表
        """
        online_devices = []
        for device in self.devices.values():
            if device.status == 'online':
                online_devices.append(device)
        return online_devices
    
    def get_available_devices(self) -> List[Device]:
        """
        获取所有可用设备（在线且不忙碌）
        
        Returns:
            List[Device]: 可用设备列表
        """
        available_devices = []
        for device in self.devices.values():
            if device.status == 'online' and device.current_task_count < device.max_concurrent_tasks:
                available_devices.append(device)
        return available_devices
    
    def get_best_device(self, task_type: str = None) -> Optional[Device]:
        """
        获取最优设备（负载最低的可用设备）
        
        Args:
            task_type: 任务类型（可用于设备选择策略）
            
        Returns:
            Device: 最优设备，无可用设备则返回None
        """
        available_devices = self.get_available_devices()
        
        if not available_devices:
            logger.warning("⚠️ 没有可用设备")
            return None
        
        # 选择负载最低的设备
        best_device = min(available_devices, key=lambda d: d.current_task_count)
        
        logger.info(f"🎯 选择最优设备: {best_device.name} (任务数: {best_device.current_task_count})")
        return best_device
    
    def update_device_status(self, device_id: str, status: str, task_count: int = None) -> bool:
        """
        更新设备状态
        
        Args:
            device_id: 设备ID
            status: 新状态 (online, offline, busy)
            task_count: 当前任务数量
            
        Returns:
            bool: 更新是否成功
        """
        try:
            if device_id in self.devices:
                device = self.devices[device_id]
                device.status = status
                device.last_heartbeat = datetime.now()
                
                if task_count is not None:
                    device.current_task_count = task_count
                
                self.device_status[device_id] = status
                logger.debug(f"📱 设备状态更新: {device.name} -> {status}")
                return True
            else:
                logger.warning(f"⚠️ 尝试更新不存在设备的状态: {device_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 更新设备状态失败: {e}")
            return False
    
    def increment_task_count(self, device_id: str) -> bool:
        """
        增加设备任务计数
        
        Args:
            device_id: 设备ID
            
        Returns:
            bool: 操作是否成功
        """
        try:
            if device_id in self.devices:
                device = self.devices[device_id]
                device.current_task_count += 1
                
                # 如果达到最大并发数，标记为忙碌
                if device.current_task_count >= device.max_concurrent_tasks:
                    device.status = 'busy'
                    self.device_status[device_id] = 'busy'
                
                logger.debug(f"📈 设备任务计数+1: {device.name} ({device.current_task_count})")
                return True
            else:
                logger.warning(f"⚠️ 尝试增加不存在设备的任务计数: {device_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 增加任务计数失败: {e}")
            return False
    
    def decrement_task_count(self, device_id: str) -> bool:
        """
        减少设备任务计数
        
        Args:
            device_id: 设备ID
            
        Returns:
            bool: 操作是否成功
        """
        try:
            if device_id in self.devices:
                device = self.devices[device_id]
                device.current_task_count = max(0, device.current_task_count - 1)
                
                # 如果任务数减少，可能从忙碌状态恢复
                if device.current_task_count < device.max_concurrent_tasks and device.status == 'busy':
                    device.status = 'online'
                    self.device_status[device_id] = 'online'
                
                logger.debug(f"📉 设备任务计数-1: {device.name} ({device.current_task_count})")
                return True
            else:
                logger.warning(f"⚠️ 尝试减少不存在设备的任务计数: {device_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 减少任务计数失败: {e}")
            return False
    
    def check_device_heartbeat(self) -> None:
        """
        检查设备心跳，标记超时设备为离线
        """
        try:
            current_time = datetime.now()
            timeout_threshold = current_time - timedelta(seconds=self.heartbeat_timeout)
            
            offline_devices = []
            
            for device_id, device in self.devices.items():
                if device.status == 'online' and device.last_heartbeat < timeout_threshold:
                    device.status = 'offline'
                    self.device_status[device_id] = 'offline'
                    offline_devices.append(device.name)
            
            if offline_devices:
                logger.warning(f"⚠️ 检测到离线设备: {', '.join(offline_devices)}")
                
        except Exception as e:
            logger.error(f"❌ 检查设备心跳失败: {e}")
    
    def get_device_statistics(self) -> Dict:
        """
        获取设备统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            total_devices = len(self.devices)
            online_devices = len([d for d in self.devices.values() if d.status == 'online'])
            busy_devices = len([d for d in self.devices.values() if d.status == 'busy'])
            offline_devices = len([d for d in self.devices.values() if d.status == 'offline'])
            total_tasks = sum(d.current_task_count for d in self.devices.values())
            
            return {
                "total_devices": total_devices,
                "online_devices": online_devices,
                "busy_devices": busy_devices,
                "offline_devices": offline_devices,
                "total_active_tasks": total_tasks,
                "average_load": total_tasks / max(1, online_devices + busy_devices)
            }
            
        except Exception as e:
            logger.error(f"❌ 获取设备统计失败: {e}")
            return {}
    
    def reset_device_tasks(self, device_id: str) -> bool:
        """
        重置设备任务计数（用于异常恢复）
        
        Args:
            device_id: 设备ID
            
        Returns:
            bool: 操作是否成功
        """
        try:
            if device_id in self.devices:
                device = self.devices[device_id]
                device.current_task_count = 0
                
                if device.status == 'busy':
                    device.status = 'online'
                    self.device_status[device_id] = 'online'
                
                logger.info(f"🔄 重置设备任务计数: {device.name}")
                return True
            else:
                logger.warning(f"⚠️ 尝试重置不存在设备的任务计数: {device_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 重置设备任务计数失败: {e}")
            return False
