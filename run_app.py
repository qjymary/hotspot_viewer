#!/usr/bin/env python3
"""
热点搜索词分析器启动脚本
"""
import subprocess
import sys
import os

def check_dependencies():
    """检查并安装必要的依赖"""
    required_packages = ['streamlit', 'plotly', 'pandas']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"⚠️ {package} 未安装，正在安装...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} 安装完成")

def main():
    print("🔥 启动热点搜索词分析器...")
    print(f"📁 工作目录: {os.getcwd()}")
    
    # 检查依赖
    check_dependencies()
    
    # 启动Streamlit应用
    print("🌐 正在启动Web应用...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "hotspot_viewer_app.py"])
    except KeyboardInterrupt:
        print("\n👋 应用已关闭")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()