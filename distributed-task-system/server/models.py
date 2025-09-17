#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
创建时间: 2025-09-17
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class Device:
    """设备模型"""
    device_id: str
    name: str
    device_type: str = "android"  # android, ios, web
    status: str = "offline"  # online, offline, busy
    last_heartbeat: Optional[datetime] = None
    registered_at: Optional[datetime] = None
    current_task_count: int = 0
    max_concurrent_tasks: int = 3  # 最大并发任务数
    device_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if self.registered_at is None:
            self.registered_at = datetime.now()
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "device_id": self.device_id,
            "name": self.name,
            "device_type": self.device_type,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "registered_at": self.registered_at.isoformat() if self.registered_at else None,
            "current_task_count": self.current_task_count,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "device_info": self.device_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Device':
        """从字典创建设备对象"""
        device = cls(
            device_id=data["device_id"],
            name=data["name"],
            device_type=data.get("device_type", "android"),
            status=data.get("status", "offline"),
            current_task_count=data.get("current_task_count", 0),
            max_concurrent_tasks=data.get("max_concurrent_tasks", 3),
            device_info=data.get("device_info", {})
        )
        
        # 处理时间字段
        if data.get("last_heartbeat"):
            device.last_heartbeat = datetime.fromisoformat(data["last_heartbeat"])
        if data.get("registered_at"):
            device.registered_at = datetime.fromisoformat(data["registered_at"])
            
        return device

@dataclass
class Task:
    """任务模型"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = ""  # DELIST, COLLECT, UPLOAD
    data: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, dispatched, running, completed, failed, cancelled
    device_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout: int = 300  # 超时时间（秒）
    progress: int = 0  # 进度百分比
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        """初始化后处理"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "data": self.data,
            "status": self.status,
            "device_id": self.device_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "timeout": self.timeout,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """从字典创建任务对象"""
        task = cls(
            task_id=data.get("task_id", str(uuid.uuid4())),
            task_type=data.get("task_type", ""),
            data=data.get("data", {}),
            status=data.get("status", "pending"),
            device_id=data.get("device_id"),
            timeout=data.get("timeout", 300),
            progress=data.get("progress", 0),
            result=data.get("result"),
            error=data.get("error"),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3)
        )
        
        # 处理时间字段
        if data.get("created_at"):
            task.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            task.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])
            
        return task
    
    def update_status(self, new_status: str, error: str = None) -> None:
        """更新任务状态"""
        self.status = new_status
        self.updated_at = datetime.now()
        
        if new_status == "running" and self.started_at is None:
            self.started_at = datetime.now()
        elif new_status in ["completed", "failed", "cancelled"] and self.completed_at is None:
            self.completed_at = datetime.now()
        
        if error:
            self.error = error
    
    def update_progress(self, progress: int) -> None:
        """更新任务进度"""
        self.progress = max(0, min(100, progress))  # 确保在0-100范围内
        self.updated_at = datetime.now()
    
    def can_retry(self) -> bool:
        """检查是否可以重试"""
        return self.retry_count < self.max_retries and self.status == "failed"
    
    def increment_retry(self) -> None:
        """增加重试次数"""
        self.retry_count += 1
        self.status = "pending"
        self.error = None
        self.updated_at = datetime.now()

@dataclass
class TaskResult:
    """任务结果模型"""
    task_id: str
    success: bool
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    processed_count: int = 0
    failed_count: int = 0
    execution_time: float = 0.0  # 执行时间（秒）
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "processed_count": self.processed_count,
            "failed_count": self.failed_count,
            "execution_time": self.execution_time,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskResult':
        """从字典创建结果对象"""
        result = cls(
            task_id=data["task_id"],
            success=data.get("success", False),
            message=data.get("message", ""),
            data=data.get("data", {}),
            processed_count=data.get("processed_count", 0),
            failed_count=data.get("failed_count", 0),
            execution_time=data.get("execution_time", 0.0)
        )
        
        if data.get("created_at"):
            result.created_at = datetime.fromisoformat(data["created_at"])
            
        return result
    
    @classmethod
    def success_result(cls, task_id: str, message: str = "任务执行成功", **kwargs) -> 'TaskResult':
        """创建成功结果"""
        return cls(
            task_id=task_id,
            success=True,
            message=message,
            **kwargs
        )
    
    @classmethod
    def error_result(cls, task_id: str, message: str = "任务执行失败", **kwargs) -> 'TaskResult':
        """创建失败结果"""
        return cls(
            task_id=task_id,
            success=False,
            message=message,
            **kwargs
        )

@dataclass
class DelistTask:
    """下架任务专用模型"""
    product_ids: list
    batch_size: int = 10
    delay_between_items: float = 1.0  # 每个商品之间的延迟（秒）
    retry_failed: bool = True
    
    def to_task_data(self) -> Dict[str, Any]:
        """转换为任务数据"""
        return {
            "product_ids": self.product_ids,
            "batch_size": self.batch_size,
            "delay_between_items": self.delay_between_items,
            "retry_failed": self.retry_failed,
            "action": "delist"
        }

@dataclass
class CollectTask:
    """采集任务专用模型"""
    target_url: str
    max_items: int = 50
    scroll_delay: float = 2.0  # 滚动延迟（秒）
    extract_images: bool = True
    extract_details: bool = True
    
    def to_task_data(self) -> Dict[str, Any]:
        """转换为任务数据"""
        return {
            "target_url": self.target_url,
            "max_items": self.max_items,
            "scroll_delay": self.scroll_delay,
            "extract_images": self.extract_images,
            "extract_details": self.extract_details,
            "action": "collect"
        }

@dataclass
class UploadTask:
    """上架任务专用模型"""
    product_data: Dict[str, Any]
    auto_publish: bool = True
    schedule_time: Optional[datetime] = None
    
    def to_task_data(self) -> Dict[str, Any]:
        """转换为任务数据"""
        return {
            "product_data": self.product_data,
            "auto_publish": self.auto_publish,
            "schedule_time": self.schedule_time.isoformat() if self.schedule_time else None,
            "action": "upload"
        }
