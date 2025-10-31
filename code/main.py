#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个人记账软件主程序入口
"""
import os
import sys
from database import db_manager
from gui import FinanceApp


def main():
    """主函数"""
    # 初始化数据库
    init_database()
    
    # 启动应用
    app = FinanceApp()
    app.mainloop()


def init_database():
    """初始化数据库"""
    try:
        # 确保数据库目录存在
        db_dir = os.path.dirname(db_manager.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # 初始化数据库
        db_manager.init_database()
        print("数据库初始化成功")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()