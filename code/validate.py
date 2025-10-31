#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证脚本
检查代码行数和基本功能是否正常
"""
import os
import sys
import sqlite3


def count_lines(file_path):
    """统计文件行数"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception as e:
        print(f"统计文件 {file_path} 行数失败: {e}")
        return 0


def check_code_lines():
    """检查所有代码文件的行数"""
    print("=== 代码行数统计 ===")
    
    python_files = ['database.py', 'user.py', 'category.py', 'transaction.py', 
                   'budget.py', 'statistics.py', 'gui.py', 'main.py']
    
    total_lines = 0
    file_lines = {}
    
    for file in python_files:
        lines = count_lines(file)
        file_lines[file] = lines
        total_lines += lines
        print(f"{file}: {lines} 行")
    
    print(f"总计: {total_lines} 行")
    
    if total_lines >= 500:
        print("✓ 代码行数满足要求（≥500行）")
    else:
        print("✗ 代码行数不满足要求（<500行）")
    
    return total_lines


def test_database_connection():
    """测试数据库连接"""
    print("\n=== 数据库连接测试 ===")
    
    try:
        # 导入数据库模块
        from database import db_manager
        
        # 初始化数据库
        db_manager.init_database()
        print("✓ 数据库初始化成功")
        
        # 测试查询
        result = db_manager.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        print(f"✓ 数据库中存在 {len(result)} 个表")
        
        # 显示所有表名
        for table in result:
            print(f"  - {table[0]}")
        
        return True
    except Exception as e:
        print(f"✗ 数据库测试失败: {e}")
        return False


def test_class_imports():
    """测试类导入"""
    print("\n=== 类导入测试 ===")
    
    try:
        # 测试所有类的导入
        from user import User
        from category import Category
        from transaction import Transaction, SearchCriteria
        from budget import Budget
        from statistics import Statistics
        
        print("✓ 所有类导入成功")
        return True
    except Exception as e:
        print(f"✗ 类导入失败: {e}")
        return False


def main():
    """主函数"""
    print("个人记账软件验证脚本\n")
    
    # 检查代码行数
    total_lines = check_code_lines()
    
    # 测试数据库连接
    db_test_passed = test_database_connection()
    
    # 测试类导入
    import_test_passed = test_class_imports()
    
    # 显示总体结果
    print("\n=== 验证结果 ===")
    if total_lines >= 500 and db_test_passed and import_test_passed:
        print("✓ 验证通过！程序可以正常运行")
        return 0
    else:
        print("✗ 验证未通过！请检查以上问题")
        return 1


if __name__ == "__main__":
    sys.exit(main())