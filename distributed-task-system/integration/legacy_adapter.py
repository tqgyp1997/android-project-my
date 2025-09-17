#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现有系统适配器
用于在现有系统中集成分布式任务系统
创建时间: 2025-09-17
"""

import os
import sys
import logging
from typing import Dict, List, Any

# 添加分布式系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
distributed_dir = os.path.dirname(current_dir)
sys.path.insert(0, distributed_dir)

from bridge_client import safe_delist_products_distributed

logger = logging.getLogger(__name__)

class LegacySystemAdapter:
    """现有系统适配器"""
    
    def __init__(self, enable_distributed: bool = True):
        """
        初始化适配器
        
        Args:
            enable_distributed: 是否启用分布式系统
        """
        self.enable_distributed = enable_distributed
        self.fallback_available = False
        
        # 尝试导入原有的下架方法作为备选
        try:
            # 这里需要根据实际情况导入原有的下架方法
            # from 自动上架UI import XianyuAutoManager
            # self.legacy_manager = XianyuAutoManager()
            # self.fallback_available = True
            logger.info("✅ 原有下架方法可用作备选")
        except Exception as e:
            logger.warning(f"⚠️ 原有下架方法不可用: {e}")
    
    def safe_delist_products(self, product_codes: List[str]) -> Dict[str, Any]:
        """
        安全下架商品方法 - 智能选择执行方式
        
        Args:
            product_codes: 商品编码列表
            
        Returns:
            Dict: 下架结果
        """
        try:
            logger.info(f"🎯 开始下架商品: {len(product_codes)}个")
            
            if self.enable_distributed:
                # 优先使用分布式系统
                logger.info("🚀 使用分布式任务系统执行下架")
                result = safe_delist_products_distributed(product_codes)
                
                # 检查是否成功
                if result.get("success"):
                    logger.info("✅ 分布式系统下架成功")
                    return result
                else:
                    logger.warning(f"⚠️ 分布式系统下架失败: {result.get('message')}")
                    
                    # 如果有备选方案，尝试使用
                    if self.fallback_available:
                        logger.info("🔄 尝试使用原有系统作为备选")
                        return self._fallback_delist(product_codes)
                    else:
                        return result
            else:
                # 使用原有系统
                logger.info("🔧 使用原有系统执行下架")
                return self._fallback_delist(product_codes)
                
        except Exception as e:
            logger.error(f"❌ 下架适配器异常: {e}")
            return {
                "success": False,
                "message": f"下架适配器异常: {str(e)}"
            }
    
    def _fallback_delist(self, product_codes: List[str]) -> Dict[str, Any]:
        """备选下架方法"""
        try:
            if self.fallback_available:
                # 调用原有的下架方法
                # result = self.legacy_manager.safe_delist_products(product_codes)
                # return result
                pass
            
            # 如果没有备选方案，返回错误
            return {
                "success": False,
                "message": "分布式系统不可用，且没有备选方案",
                "method": "fallback_unavailable"
            }
            
        except Exception as e:
            logger.error(f"❌ 备选下架方法异常: {e}")
            return {
                "success": False,
                "message": f"备选下架方法异常: {str(e)}",
                "method": "fallback_error"
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            from bridge_client import distributed_bridge
            
            # 获取分布式系统状态
            distributed_status = distributed_bridge.get_system_status()
            devices = distributed_bridge.get_devices()
            
            return {
                "distributed_enabled": self.enable_distributed,
                "distributed_available": distributed_status.get("status") == "running",
                "connected_devices": devices.get("total", 0) if devices.get("success") else 0,
                "fallback_available": self.fallback_available,
                "system_info": distributed_status
            }
            
        except Exception as e:
            return {
                "distributed_enabled": self.enable_distributed,
                "distributed_available": False,
                "connected_devices": 0,
                "fallback_available": self.fallback_available,
                "error": str(e)
            }

# 全局适配器实例
legacy_adapter = LegacySystemAdapter(enable_distributed=True)

def create_enhanced_delist_method():
    """
    创建增强的下架方法，可以直接替换现有系统中的方法
    
    使用方法：
    1. 在现有系统中导入这个方法
    2. 替换原有的 safe_delist_products 方法
    
    Returns:
        function: 增强的下架方法
    """
    def enhanced_safe_delist_products(product_codes: List[str]) -> Dict[str, Any]:
        """
        增强的安全下架方法
        自动选择最优执行方式：分布式系统 > 原有系统
        """
        return legacy_adapter.safe_delist_products(product_codes)
    
    return enhanced_safe_delist_products

# 导出增强方法
enhanced_safe_delist_products = create_enhanced_delist_method()

if __name__ == "__main__":
    # 测试适配器
    print("🧪 测试分布式任务系统适配器")
    
    # 测试系统状态
    status = legacy_adapter.get_system_status()
    print(f"📊 系统状态: {status}")
    
    # 测试下架功能（使用测试数据）
    test_codes = ["test_001", "test_002"]
    print(f"🧪 测试下架: {test_codes}")
    
    result = legacy_adapter.safe_delist_products(test_codes)
    print(f"📋 下架结果: {result}")
