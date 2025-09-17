#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分布式任务系统集成桥接器
用于现有系统调用分布式任务系统
创建时间: 2025-09-17
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DistributedTaskBridge:
    """分布式任务系统桥接器"""
    
    def __init__(self, server_url: str = "http://localhost:1888"):
        """
        初始化桥接器
        
        Args:
            server_url: 分布式任务系统服务器地址
        """
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
        
        # 测试连接
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """测试与分布式任务系统的连接"""
        try:
            response = self.session.get(f"{self.server_url}/")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ 连接分布式任务系统成功: {data.get('system', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ 连接分布式任务系统失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 连接分布式任务系统异常: {e}")
            return False
    
    def dispatch_delist_task(self, product_codes: List[str], device_id: str = None) -> Dict[str, Any]:
        """
        分发下架任务到分布式系统
        
        Args:
            product_codes: 商品编码列表
            device_id: 指定设备ID（可选）
            
        Returns:
            Dict: 任务分发结果
        """
        try:
            logger.info(f"📤 分发下架任务: {len(product_codes)}个商品")
            
            # 构造任务数据
            task_data = {
                "task_type": "DELIST",
                "data": {
                    "product_ids": product_codes,
                    "batch_size": len(product_codes),
                    "delay_between_items": 1.0,
                    "retry_failed": True,
                    "action": "delist"
                }
            }
            
            if device_id:
                task_data["device_id"] = device_id
            
            # 发送任务
            response = self.session.post(
                f"{self.server_url}/api/dispatch-task",
                json=task_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"✅ 下架任务分发成功: {result.get('task_id')}")
                    return {
                        "success": True,
                        "task_id": result.get("task_id"),
                        "device_id": result.get("device_id"),
                        "device_name": result.get("device_name"),
                        "message": "任务已分发到分布式系统"
                    }
                else:
                    logger.error(f"❌ 下架任务分发失败: {result.get('message')}")
                    return {
                        "success": False,
                        "message": result.get("message", "分发失败")
                    }
            else:
                logger.error(f"❌ HTTP请求失败: {response.status_code}")
                return {
                    "success": False,
                    "message": f"HTTP请求失败: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ 分发下架任务异常: {e}")
            return {
                "success": False,
                "message": f"分发任务异常: {str(e)}"
            }
    
    def wait_for_task_completion(self, task_id: str, timeout: int = 300) -> Dict[str, Any]:
        """
        等待任务完成
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）
            
        Returns:
            Dict: 任务结果
        """
        try:
            logger.info(f"⏳ 等待任务完成: {task_id}")
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # 查询任务状态
                response = self.session.get(f"{self.server_url}/api/task/{task_id}/status")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        task_info = result.get("task", {})
                        status = task_info.get("status")
                        
                        if status == "completed":
                            logger.info(f"✅ 任务完成: {task_id}")
                            return {
                                "success": True,
                                "status": "completed",
                                "result": task_info.get("result", {}),
                                "progress": task_info.get("progress", 100)
                            }
                        elif status == "failed":
                            logger.error(f"❌ 任务失败: {task_id}")
                            return {
                                "success": False,
                                "status": "failed",
                                "error": task_info.get("error", "任务执行失败"),
                                "progress": task_info.get("progress", 0)
                            }
                        elif status in ["pending", "dispatched", "running"]:
                            # 任务还在执行中
                            progress = task_info.get("progress", 0)
                            logger.debug(f"📊 任务进度: {task_id} - {progress}%")
                            time.sleep(2)  # 等待2秒后再次查询
                            continue
                        else:
                            logger.warning(f"⚠️ 未知任务状态: {status}")
                            time.sleep(2)
                            continue
                    else:
                        logger.error(f"❌ 查询任务状态失败: {result.get('message')}")
                        return {
                            "success": False,
                            "message": result.get("message", "查询失败")
                        }
                else:
                    logger.error(f"❌ HTTP请求失败: {response.status_code}")
                    time.sleep(2)
                    continue
            
            # 超时
            logger.error(f"⏰ 任务等待超时: {task_id}")
            return {
                "success": False,
                "message": "任务等待超时"
            }
            
        except Exception as e:
            logger.error(f"❌ 等待任务完成异常: {e}")
            return {
                "success": False,
                "message": f"等待任务异常: {str(e)}"
            }
    
    def delist_products_sync(self, product_codes: List[str], device_id: str = None, timeout: int = 300) -> Dict[str, Any]:
        """
        同步下架商品（分发任务并等待完成）
        
        Args:
            product_codes: 商品编码列表
            device_id: 指定设备ID（可选）
            timeout: 超时时间（秒）
            
        Returns:
            Dict: 下架结果
        """
        try:
            logger.info(f"🚀 开始同步下架: {len(product_codes)}个商品")
            
            # 1. 分发任务
            dispatch_result = self.dispatch_delist_task(product_codes, device_id)
            if not dispatch_result.get("success"):
                return dispatch_result
            
            task_id = dispatch_result.get("task_id")
            
            # 2. 等待任务完成
            completion_result = self.wait_for_task_completion(task_id, timeout)
            
            # 3. 整合结果
            if completion_result.get("success"):
                task_result = completion_result.get("result", {})
                return {
                    "success": True,
                    "message": "下架任务完成",
                    "task_id": task_id,
                    "device_id": dispatch_result.get("device_id"),
                    "device_name": dispatch_result.get("device_name"),
                    "processed_count": task_result.get("processed_count", 0),
                    "failed_count": task_result.get("failed_count", 0),
                    "execution_time": task_result.get("execution_time", 0),
                    "details": task_result.get("data", {})
                }
            else:
                return {
                    "success": False,
                    "message": completion_result.get("message", "任务执行失败"),
                    "task_id": task_id,
                    "error": completion_result.get("error")
                }
                
        except Exception as e:
            logger.error(f"❌ 同步下架异常: {e}")
            return {
                "success": False,
                "message": f"同步下架异常: {str(e)}"
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取分布式系统状态"""
        try:
            response = self.session.get(f"{self.server_url}/")
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_devices(self) -> Dict[str, Any]:
        """获取设备列表"""
        try:
            response = self.session.get(f"{self.server_url}/api/devices")
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_tasks(self) -> Dict[str, Any]:
        """获取任务列表"""
        try:
            response = self.session.get(f"{self.server_url}/api/tasks")
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

# 全局桥接器实例
distributed_bridge = DistributedTaskBridge()

def safe_delist_products_distributed(product_codes: List[str], device_id: str = None) -> Dict[str, Any]:
    """
    使用分布式系统下架商品的安全方法
    这个方法可以直接替换现有的 safe_delist_products 方法
    
    Args:
        product_codes: 商品编码列表
        device_id: 指定设备ID（可选）
        
    Returns:
        Dict: 下架结果，格式与原方法兼容
    """
    try:
        logger.info(f"🔄 使用分布式系统下架商品: {len(product_codes)}个")
        
        # 调用分布式系统
        result = distributed_bridge.delist_products_sync(product_codes, device_id)
        
        # 转换为兼容格式
        if result.get("success"):
            return {
                "success": True,
                "message": result.get("message", "下架完成"),
                "processed_count": result.get("processed_count", 0),
                "failed_count": result.get("failed_count", 0),
                "task_id": result.get("task_id"),
                "device_info": {
                    "device_id": result.get("device_id"),
                    "device_name": result.get("device_name")
                },
                "execution_time": result.get("execution_time", 0),
                "method": "distributed_system"  # 标识使用了分布式系统
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "下架失败"),
                "error": result.get("error"),
                "method": "distributed_system"
            }
            
    except Exception as e:
        logger.error(f"❌ 分布式下架异常: {e}")
        return {
            "success": False,
            "message": f"分布式下架异常: {str(e)}",
            "method": "distributed_system"
        }
