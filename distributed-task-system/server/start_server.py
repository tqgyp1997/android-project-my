#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分布式任务系统 - 服务器启动脚本
创建时间: 2025-09-17
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查依赖包...")
    
    try:
        import flask
        import flask_socketio
        import flask_cors
        print("✅ 核心依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("📦 正在安装依赖...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("✅ 依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败")
            return False

def check_port(port=1888):
    """检查端口是否被占用"""
    print(f"🔍 检查端口 {port}...")
    
    try:
        response = requests.get(f"http://localhost:{port}", timeout=2)
        print(f"⚠️ 端口 {port} 已被占用")
        return False
    except requests.exceptions.RequestException:
        print(f"✅ 端口 {port} 可用")
        return True

def start_server():
    """启动服务器"""
    print("🚀 启动分布式任务系统服务器...")
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 检查端口
    if not check_port():
        choice = input("端口被占用，是否强制启动？(y/n): ")
        if choice.lower() != 'y':
            return False
    
    # 启动服务器
    try:
        print("=" * 50)
        print("🎯 分布式任务系统")
        print("📡 端口: 1888")
        print("🌐 管理地址: http://localhost:1888")
        print("📱 设备连接: ws://localhost:1888")
        print("=" * 50)
        
        # 导入并启动应用
        from app import app, socketio
        socketio.run(app, host='0.0.0.0', port=1888, debug=False)
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        return True
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def show_help():
    """显示帮助信息"""
    print("""
🎯 分布式任务系统 - 启动脚本

用法:
    python start_server.py [选项]

选项:
    --help, -h      显示此帮助信息
    --check         仅检查环境，不启动服务器
    --install       仅安装依赖
    --port PORT     指定端口（默认1888）

示例:
    python start_server.py              # 启动服务器
    python start_server.py --check      # 检查环境
    python start_server.py --port 8888  # 使用8888端口
    """)

def main():
    """主函数"""
    args = sys.argv[1:]
    
    if '--help' in args or '-h' in args:
        show_help()
        return
    
    if '--check' in args:
        print("🔍 环境检查...")
        deps_ok = check_dependencies()
        port_ok = check_port()
        
        if deps_ok and port_ok:
            print("✅ 环境检查通过")
        else:
            print("❌ 环境检查失败")
        return
    
    if '--install' in args:
        check_dependencies()
        return
    
    # 处理端口参数
    port = 1888
    if '--port' in args:
        try:
            port_index = args.index('--port')
            if port_index + 1 < len(args):
                port = int(args[port_index + 1])
        except (ValueError, IndexError):
            print("❌ 端口参数无效")
            return
    
    # 启动服务器
    start_server()

if __name__ == '__main__':
    main()
