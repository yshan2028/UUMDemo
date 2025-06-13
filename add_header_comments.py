#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import datetime
from pathlib import Path


def create_file_header(file_path, author="yshan2028"):
    """
    创建文件头注释模板

    Args:
        file_path: 文件路径
        author: 作者名称

    Returns:
        str: 格式化的文件头注释
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = os.path.basename(file_path)

    header = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: {file_name}
Author: {author}
Created: {current_time}
Description: 
    [请在此处添加文件描述]

Dependencies:
    [请在此处列出主要依赖]

Usage:
    [请在此处添加使用说明]
"""

'''
    return header


def has_header_comment(file_content):
    """
    检查文件是否已经有头部注释

    Args:
        file_content: 文件内容

    Returns:
        bool: 是否已有头部注释
    """
    lines = file_content.split('\n')

    # 检查是否已有 shebang 和编码声明
    has_shebang = any(line.startswith('#!') for line in lines[:5])
    has_encoding = any('coding' in line or 'encoding' in line for line in lines[:5])
    has_docstring = '"""' in file_content[:500] or "'''" in file_content[:500]

    return has_shebang and has_encoding and has_docstring


def add_header_to_file(file_path, author="yshan2028", dry_run=False):
    """
    给单个文件添加头部注释

    Args:
        file_path: 文件路径
        author: 作者名称
        dry_run: 是否为演练模式（不实际修改文件）

    Returns:
        bool: 是否成功添加头部注释
    """
    try:
        # 读取原文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # 检查是否已有头部注释
        if has_header_comment(original_content):
            print(f"SKIP: {file_path} - Already has header comment")
            return False

        # 创建新的文件头
        header = create_file_header(file_path, author)

        # 合并内容
        new_content = header + original_content

        if dry_run:
            print(f"DRY RUN: Would add header to {file_path}")
            return True

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"SUCCESS: Added header to {file_path}")
        return True

    except Exception as e:
        print(f"ERROR: Failed to process {file_path} - {str(e)}")
        return False


def find_python_files(root_dir, exclude_dirs=None):
    """
    查找指定目录下的所有 Python 文件

    Args:
        root_dir: 根目录
        exclude_dirs: 要排除的目录列表

    Returns:
        list: Python 文件路径列表
    """
    if exclude_dirs is None:
        exclude_dirs = ['__pycache__', '.git', '.pytest_cache', 'venv', 'env', '.venv']

    python_files = []

    for root, dirs, files in os.walk(root_dir):
        # 排除指定目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                python_files.append(file_path)

    return python_files


def main():
    """
    主函数
    """
    print("=" * 60)
    print("Python File Header Comment Generator")
    print("=" * 60)

    # 配置选项
    root_directory = input("请输入项目根目录路径 (默认为当前目录): ").strip()
    if not root_directory:
        root_directory = "."

    author_name = input("请输入作者名称 (默认: yshan2028): ").strip()
    if not author_name:
        author_name = "yshan2028"

    # 询问是否先进行演练
    dry_run_choice = input("是否先进行演练？(y/n, 默认: y): ").strip().lower()
    dry_run = dry_run_choice != 'n'

    # 检查目录是否存在
    if not os.path.exists(root_directory):
        print(f"错误: 目录 '{root_directory}' 不存在")
        return

    # 查找所有 Python 文件
    print(f"\n正在搜索 Python 文件...")
    python_files = find_python_files(root_directory)

    if not python_files:
        print("未找到任何 Python 文件")
        return

    print(f"找到 {len(python_files)} 个 Python 文件:")
    for file_path in python_files:
        print(f"  - {file_path}")

    # 确认是否继续
    if dry_run:
        print(f"\n开始演练模式...")
    else:
        confirm = input(f"\n是否继续为这 {len(python_files)} 个文件添加头部注释？(y/n): ").strip().lower()
        if confirm != 'y':
            print("操作已取消")
            return

    # 处理文件
    print("\n开始处理文件...")
    success_count = 0
    skip_count = 0
    error_count = 0

    for file_path in python_files:
        result = add_header_to_file(file_path, author_name, dry_run)
        if result:
            success_count += 1
        else:
            if has_header_comment(open(file_path, 'r', encoding='utf-8').read()):
                skip_count += 1
            else:
                error_count += 1

    # 显示结果统计
    print("\n" + "=" * 60)
    print("处理完成！")
    print(f"成功处理: {success_count} 个文件")
    print(f"跳过文件: {skip_count} 个文件 (已有头部注释)")
    print(f"错误文件: {error_count} 个文件")
    print("=" * 60)

    # 如果是演练模式，询问是否正式执行
    if dry_run and success_count > 0:
        execute_choice = input("\n演练完成，是否正式执行添加头部注释？(y/n): ").strip().lower()
        if execute_choice == 'y':
            print("\n开始正式执行...")
            success_count = 0
            for file_path in python_files:
                result = add_header_to_file(file_path, author_name, dry_run=False)
                if result:
                    success_count += 1
            print(f"\n正式执行完成！成功处理 {success_count} 个文件")


if __name__ == "__main__":
    main()