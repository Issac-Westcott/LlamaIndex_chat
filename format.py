#!/usr/bin/env python3
"""
统一代码格式化脚本（Python 版本）
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """运行命令并处理错误"""
    print(f"📝 {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=False,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ {description} 完成")
            return True
        else:
            print(f"⚠️  {description} 失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"⚠️  {description} 出错: {e}")
        return False

def format_python():
    """格式化 Python 代码"""
    print("\n🐍 格式化 Python 代码...")
    
    # 检查是否使用 uv
    if os.system("command -v uv > /dev/null 2>&1") == 0:
        print("使用 uv 运行格式化工具...")
        
        # 安装格式化工具（如果未安装）
        subprocess.run("uv pip install black ruff isort --quiet", shell=True)
        
        # 运行 black
        run_command("uv run black app/ main.py --line-length 100", "Black 格式化")
        
        # 运行 isort
        run_command("uv run isort app/ main.py --profile black --line-length 100", "isort 排序导入")
        
        # 运行 ruff format
        run_command("uv run ruff format app/ main.py --line-length 100", "Ruff 格式化")
    else:
        # 使用系统 Python
        run_command("black app/ main.py --line-length 100", "Black 格式化")
        run_command("isort app/ main.py --profile black --line-length 100", "isort 排序导入")

def format_frontend():
    """格式化前端代码"""
    print("\n🎨 格式化前端代码...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("⚠️  前端目录不存在")
        return
    
    os.chdir(frontend_dir)
    
    # 检查是否使用 pnpm
    use_pnpm = os.system("command -v pnpm > /dev/null 2>&1") == 0
    
    # 检查 node_modules
    if not Path("node_modules").exists():
        if use_pnpm:
            print("使用 pnpm 安装前端依赖...")
            subprocess.run("pnpm install --silent", shell=True)
        else:
            print("使用 npm 安装前端依赖...")
            subprocess.run("npm install --silent", shell=True)
    
    # 运行 Prettier
    if use_pnpm:
        run_command("pnpm run format", "Prettier 格式化")
    else:
        run_command("npm run format", "Prettier 格式化")
    
    os.chdir("..")

def main():
    """主函数"""
    print("🚀 开始格式化代码...\n")
    
    # 格式化 Python
    format_python()
    
    # 格式化前端
    format_frontend()
    
    print("\n✅ 代码格式化完成！")

if __name__ == "__main__":
    main()
