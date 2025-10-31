#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户模块
实现用户相关的业务逻辑
"""
import hashlib
import uuid
from database import db_manager


class User:
    """用户类，负责用户信息管理和身份验证"""

    def __init__(self, user_id=None, username=None, password=None, monthly_budget=0):
        """初始化用户对象"""
        self.user_id = user_id
        self.username = username
        self.password = password  # 存储加密后的密码
        self.monthly_budget = monthly_budget

    @staticmethod
    def _hash_password(password):
        """对密码进行加密处理"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self):
        """注册新用户
        
        Returns:
            bool: 注册是否成功
        """
        try:
            # 检查用户名是否已存在
            existing_user = db_manager.execute_query(
                "SELECT user_id FROM users WHERE username = ?",
                (self.username,)
            )
            
            if existing_user:
                return False  # 用户名已存在
            
            # 生成用户ID
            self.user_id = str(uuid.uuid4())
            # 加密密码
            hashed_password = self._hash_password(self.password)
            
            # 插入用户数据
            db_manager.execute_query(
                '''INSERT INTO users (user_id, username, password, monthly_budget) 
                VALUES (?, ?, ?, ?)''',
                (self.user_id, self.username, hashed_password, self.monthly_budget),
                commit=True
            )
            
            return True
        except Exception as e:
            print(f"注册失败: {e}")
            return False

    def login(self):
        """用户登录
        
        Returns:
            bool: 登录是否成功
        """
        try:
            # 查询用户信息
            user_data = db_manager.execute_query(
                "SELECT user_id, password, monthly_budget FROM users WHERE username = ?",
                (self.username,)
            )
            
            if not user_data:
                return False  # 用户不存在
            
            stored_user_id, stored_password, stored_budget = user_data[0]
            # 验证密码
            if self._hash_password(self.password) != stored_password:
                return False  # 密码错误
            
            # 更新用户对象信息
            self.user_id = stored_user_id
            self.monthly_budget = stored_budget
            
            return True
        except Exception as e:
            print(f"登录失败: {e}")
            return False

    def set_budget(self, budget_amount):
        """设置月度预算
        
        Args:
            budget_amount: 预算金额
        """
        try:
            self.monthly_budget = budget_amount
            db_manager.execute_query(
                "UPDATE users SET monthly_budget = ? WHERE user_id = ?",
                (budget_amount, self.user_id),
                commit=True
            )
            return True
        except Exception as e:
            print(f"设置预算失败: {e}")
            return False

    def check_overspending(self, month=None):
        """检查是否超支
        
        Args:
            month: 指定月份，格式为'YYYY-MM'
        
        Returns:
            bool: 是否超支
        """
        try:
            # 如果没有指定月份，使用当前月份
            if not month:
                from datetime import datetime
                month = datetime.now().strftime('%Y-%m')
            
            # 查询该月总支出
            total_expense = db_manager.execute_query(
                '''SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE user_id = ? AND type = '支出' AND date LIKE ?''',
                (self.user_id, f"{month}%"),
            )[0][0]
            
            # 先检查是否有月度预算设置
            budget_data = db_manager.execute_query(
                "SELECT amount FROM budgets WHERE user_id = ? AND month = ?",
                (self.user_id, month)
            )
            
            if budget_data:
                budget_amount = budget_data[0][0]
            else:
                budget_amount = self.monthly_budget
            
            return total_expense > budget_amount
        except Exception as e:
            print(f"检查超支失败: {e}")
            return False

    @staticmethod
    def get_user_by_id(user_id):
        """根据用户ID获取用户信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            User: 用户对象
        """
        try:
            user_data = db_manager.execute_query(
                "SELECT user_id, username, monthly_budget FROM users WHERE user_id = ?",
                (user_id,)
            )
            
            if not user_data:
                return None
            
            user_id, username, monthly_budget = user_data[0]
            return User(user_id=user_id, username=username, monthly_budget=monthly_budget)
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None