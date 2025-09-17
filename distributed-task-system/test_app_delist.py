#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APP下架功能测试脚本
用于测试新增的APP下架功能
创建时间: 2025-09-17
"""

import requests
import json
import time
from typing import List, Dict, Any

def test_distributed_system_status():
    """测试分布式系统状态"""
    print("🔍 测试分布式系统状态...")
    
    try:
        # 直接访问分布式系统
        response = requests.get("http://localhost:1888/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 分布式系统运行正常")
            print(f"   - 系统: {data.get('system')}")
            print(f"   - 状态: {data.get('status')}")
            print(f"   - 端口: {data.get('port')}")
            print(f"   - 连接设备: {data.get('connected_devices')}")
            print(f"   - 活跃任务: {data.get('active_tasks')}")
            return True
        else:
            print(f"❌ 分布式系统响应异常: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 分布式系统连接失败: {e}")
        return False

def test_distributed_status_api():
    """测试分布式系统状态API"""
    print("\n🔍 测试分布式系统状态API...")
    
    try:
        response = requests.get("http://localhost:1887/xianyu-center-api/delisting/distributed-status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ 分布式系统状态API正常")
                system_data = data.get("data", {})
                system_status = system_data.get("system_status", {})
                devices = system_data.get("devices", {})
                
                print(f"   - 系统状态: {system_status.get('status')}")
                print(f"   - 连接设备: {devices.get('total', 0)}")
                print(f"   - 查询时间: {system_data.get('query_time')}")
                return True
            else:
                print(f"❌ 分布式系统状态API失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 分布式系统状态API响应异常: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 分布式系统状态API连接失败: {e}")
        return False

def test_app_delist_api(product_codes: List[str]):
    """测试APP下架API"""
    print(f"\n🧪 测试APP下架API: {product_codes}")
    
    try:
        # 构造请求数据
        request_data = {
            "product_codes": product_codes
        }
        
        # 发送请求
        response = requests.post(
            "http://localhost:1887/xianyu-center-api/delisting/app-delist",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ APP下架API调用成功")
                result_data = data.get("data", {})
                print(f"   - 处理数量: {result_data.get('processed_count', 0)}")
                print(f"   - 失败数量: {result_data.get('failed_count', 0)}")
                print(f"   - 执行时间: {result_data.get('execution_time', 0)}秒")
                print(f"   - 任务ID: {result_data.get('task_id')}")
                print(f"   - 执行方式: {result_data.get('method')}")
                
                device_info = result_data.get('device_info', {})
                if device_info:
                    print(f"   - 执行设备: {device_info.get('device_name', '未知')}")
                
                return True
            else:
                print(f"❌ APP下架API失败: {data.get('message')}")
                error_data = data.get("data", {})
                if error_data.get("method"):
                    print(f"   - 执行方式: {error_data.get('method')}")
                if error_data.get("error"):
                    print(f"   - 错误详情: {error_data.get('error')}")
                return False
        else:
            print(f"❌ APP下架API响应异常: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   - 错误信息: {error_data}")
            except:
                print(f"   - 响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ APP下架API连接失败: {e}")
        return False

def test_bridge_client_directly():
    """直接测试桥接客户端"""
    print("\n🔧 直接测试桥接客户端...")
    
    try:
        import sys
        import os
        
        # 添加路径
        bridge_path = os.path.join(os.path.dirname(__file__), 'integration')
        if bridge_path not in sys.path:
            sys.path.append(bridge_path)
        
        from bridge_client import safe_delist_products_distributed
        
        # 测试下架
        test_codes = ["test_bridge_001", "test_bridge_002"]
        print(f"🧪 测试商品编码: {test_codes}")
        
        result = safe_delist_products_distributed(test_codes)
        
        if result.get("success"):
            print("✅ 桥接客户端测试成功")
            print(f"   - 处理数量: {result.get('processed_count', 0)}")
            print(f"   - 失败数量: {result.get('failed_count', 0)}")
            print(f"   - 任务ID: {result.get('task_id')}")
            print(f"   - 设备信息: {result.get('device_info', {})}")
        else:
            print(f"❌ 桥接客户端测试失败: {result.get('message')}")
            print(f"   - 错误: {result.get('error')}")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ 桥接客户端测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始APP下架功能测试")
    print("=" * 50)
    
    # 测试计数
    total_tests = 0
    passed_tests = 0
    
    # 1. 测试分布式系统状态
    total_tests += 1
    if test_distributed_system_status():
        passed_tests += 1
    
    # 2. 测试分布式系统状态API
    total_tests += 1
    if test_distributed_status_api():
        passed_tests += 1
    
    # 3. 测试桥接客户端
    total_tests += 1
    if test_bridge_client_directly():
        passed_tests += 1
    
    # 4. 测试APP下架API
    total_tests += 1
    test_product_codes = ["test_app_001", "test_app_002", "test_app_003"]
    if test_app_delist_api(test_product_codes):
        passed_tests += 1
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！APP下架功能集成成功！")
        print("\n💡 使用建议:")
        print("1. 原有下架方法保持不变，继续使用 safe_delist_products()")
        print("2. 新增APP下架方法可用，使用 safe_delist_products_app()")
        print("3. API接口: POST /xianyu-center-api/delisting/app-delist")
        print("4. 状态查询: GET /xianyu-center-api/delisting/distributed-status")
    else:
        print("⚠️ 部分测试失败，请检查:")
        print("1. 分布式任务系统是否正常运行 (端口1888)")
        print("2. 现有系统是否正常运行 (端口1887)")
        print("3. 是否有Android设备连接到分布式系统")
        print("4. 网络连接是否正常")
    
    print("\n🔗 相关链接:")
    print("- 分布式系统: http://localhost:1888")
    print("- 现有系统: http://localhost:1887/admin#")
    print("- 集成文档: distributed-task-system/integration/INTEGRATION_GUIDE.md")

if __name__ == "__main__":
    main()
