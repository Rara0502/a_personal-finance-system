#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记账软件数据库模块
负责本地数据存储和访问
"""
import sqlite3
import json
from datetime import datetime


class DatabaseManager:
    """数据库管理器，负责所有数据的存储和检索"""

    def __init__(self, db_path='finance_app.db'):
        """初始化数据库连接"""
        self.db_path = db_path
        self._init_database()
        
    def init_database(self):
        """初始化数据库，创建必要的数据表"""
        # 调用现有的私有初始化方法
        self._init_database()

    def _init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            monthly_budget REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 创建分类表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            category_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,  -- 收入类/支出类
            icon TEXT,
            is_custom INTEGER DEFAULT 0,
            user_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )
        ''')

        # 创建交易记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            amount REAL NOT NULL,
            type TEXT NOT NULL,  -- 收入/支出
            category_id TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (category_id),
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )
        ''')

        # 创建预算表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            budget_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            month TEXT NOT NULL,
            amount REAL NOT NULL,
            spent REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
            UNIQUE (user_id, month)
        )
        ''')

        # 插入预设分类
        self._insert_default_categories(cursor)

        conn.commit()
        conn.close()

    def _insert_default_categories(self, cursor):
        """插入默认分类"""
        default_categories = [
            # 支出类
            ('cat_1', '餐饮', '支出类', '📋', 0, None),
            ('cat_2', '交通', '支出类', '🚗', 0, None),
            ('cat_3', '购物', '支出类', '🎁', 0, None),
            ('cat_4', '娱乐', '支出类', '🎮', 0, None),
            ('cat_5', '医疗', '支出类', '🏥', 0, None),
            ('cat_6', '教育', '支出类', '📚', 0, None),
            ('cat_7', '居住', '支出类', '🏠', 0, None),
            ('cat_8', '其他支出', '支出类', '📋', 0, None),
            # 收入类
            ('cat_9', '工资', '收入类', '💰', 0, None),
            ('cat_10', '奖金', '收入类', '🎁', 0, None),
            ('cat_11', '投资收益', '收入类', '📈', 0, None),
            ('cat_12', '其他收入', '收入类', '💵', 0, None),
        ]

        cursor.executemany(
            '''INSERT OR IGNORE INTO categories 
            (category_id, name, type, icon, is_custom, user_id) 
            VALUES (?, ?, ?, ?, ?, ?)''',
            default_categories
        )

    def connect(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def execute_query(self, query, params=(), commit=False):
        """执行SQL查询"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if commit:
            conn.commit()
            result = None
        else:
            result = cursor.fetchall()
        
        conn.close()
        return result

    def execute_many(self, query, params_list, commit=True):
        """批量执行SQL查询"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        
        if commit:
            conn.commit()
        
        conn.close()


# 数据库单例实例
db_manager = DatabaseManager()