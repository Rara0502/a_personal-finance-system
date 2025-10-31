#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分类模块
实现分类相关的业务逻辑
"""
import uuid
from database import db_manager


class Category:
    """分类类，负责分类信息管理"""

    def __init__(self, category_id=None, name=None, type=None, icon=None, is_custom=False, user_id=None):
        """初始化分类对象"""
        self.category_id = category_id
        self.name = name
        self.type = type  # 收入类/支出类
        self.icon = icon
        self.is_custom = is_custom
        self.user_id = user_id

    def add_custom_category(self):
        """添加自定义分类
        
        Returns:
            bool: 添加是否成功
        """
        try:
            # 生成分类ID
            self.category_id = str(uuid.uuid4())
            self.is_custom = True
            
            # 插入分类数据
            db_manager.execute_query(
                '''INSERT INTO categories (category_id, name, type, icon, is_custom, user_id) 
                VALUES (?, ?, ?, ?, ?, ?)''',
                (self.category_id, self.name, self.type, self.icon, 1, self.user_id),
                commit=True
            )
            
            return True
        except Exception as e:
            print(f"添加自定义分类失败: {e}")
            return False

    @staticmethod
    def get_preset_categories(type=None):
        """获取预设分类列表
        
        Args:
            type: 分类类型过滤，可以是'收入类'或'支出类'
        
        Returns:
            list: 分类对象列表
        """
        try:
            query = "SELECT category_id, name, type, icon FROM categories WHERE is_custom = 0"
            params = []
            
            if type:
                query += " AND type = ?"
                params.append(type)
            
            categories_data = db_manager.execute_query(query, params)
            
            categories = []
            for data in categories_data:
                category = Category(
                    category_id=data[0],
                    name=data[1],
                    type=data[2],
                    icon=data[3],
                    is_custom=False
                )
                categories.append(category)
            
            return categories
        except Exception as e:
            print(f"获取预设分类失败: {e}")
            return []

    @staticmethod
    def get_all_categories(user_id=None, type=None):
        """获取所有分类（包括预设和自定义）
        
        Args:
            user_id: 用户ID，用于获取用户自定义分类
            type: 分类类型过滤
        
        Returns:
            list: 分类对象列表
        """
        try:
            # 构建查询
            query = "SELECT category_id, name, type, icon, is_custom FROM categories WHERE 1=1"
            params = []
            
            # 添加用户条件
            if user_id:
                query += " AND (user_id IS NULL OR user_id = ?)"
                params.append(user_id)
            else:
                query += " AND user_id IS NULL"
            
            # 添加类型条件
            if type:
                query += " AND type = ?"
                params.append(type)
            
            categories_data = db_manager.execute_query(query, params)
            
            categories = []
            for data in categories_data:
                category = Category(
                    category_id=data[0],
                    name=data[1],
                    type=data[2],
                    icon=data[3],
                    is_custom=bool(data[4])
                )
                categories.append(category)
            
            return categories
        except Exception as e:
            print(f"获取分类列表失败: {e}")
            return []

    def update(self):
        """更新分类信息
        
        Returns:
            bool: 更新是否成功
        """
        try:
            # 只能更新自定义分类
            if not self.is_custom:
                return False
            
            db_manager.execute_query(
                "UPDATE categories SET name = ?, icon = ? WHERE category_id = ? AND user_id = ?",
                (self.name, self.icon, self.category_id, self.user_id),
                commit=True
            )
            
            return True
        except Exception as e:
            print(f"更新分类失败: {e}")
            return False

    def delete(self):
        """删除自定义分类
        
        Returns:
            bool: 删除是否成功
        """
        try:
            # 只能删除自定义分类
            if not self.is_custom:
                return False
            
            # 检查是否有交易记录使用该分类
            count = db_manager.execute_query(
                "SELECT COUNT(*) FROM transactions WHERE category_id = ?",
                (self.category_id,)
            )[0][0]
            
            if count > 0:
                return False  # 有交易记录使用该分类，不能删除
            
            db_manager.execute_query(
                "DELETE FROM categories WHERE category_id = ? AND user_id = ?",
                (self.category_id, self.user_id),
                commit=True
            )
            
            return True
        except Exception as e:
            print(f"删除分类失败: {e}")
            return False

    @staticmethod
    def get_category_by_id(category_id):
        """根据ID获取分类信息
        
        Args:
            category_id: 分类ID
        
        Returns:
            Category: 分类对象
        """
        try:
            category_data = db_manager.execute_query(
                "SELECT category_id, name, type, icon, is_custom, user_id FROM categories WHERE category_id = ?",
                (category_id,)
            )
            
            if not category_data:
                return None
            
            data = category_data[0]
            return Category(
                category_id=data[0],
                name=data[1],
                type=data[2],
                icon=data[3],
                is_custom=bool(data[4]),
                user_id=data[5]
            )
        except Exception as e:
            print(f"获取分类信息失败: {e}")
            return None