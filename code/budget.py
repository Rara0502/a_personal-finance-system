#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预算模块
实现预算相关的业务逻辑
"""
import uuid
from database import db_manager


class Budget:
    """预算类，负责预算信息管理"""

    def __init__(self, budget_id=None, user_id=None, month=None, amount=0, spent=0):
        """初始化预算对象"""
        self.budget_id = budget_id
        self.user_id = user_id
        self.month = month
        self.amount = amount
        self.spent = spent
        
        # 如果提供了user_id和month，尝试从数据库加载预算信息
        if user_id and month:
            self._load_budget()

    def _load_budget(self):
        """从数据库加载预算信息"""
        try:
            budget_data = db_manager.execute_query(
                "SELECT budget_id, amount, spent FROM budgets WHERE user_id = ? AND month = ?",
                (self.user_id, self.month)
            )
            
            if budget_data:
                self.budget_id = budget_data[0][0]
                self.amount = budget_data[0][1]
                self.spent = budget_data[0][2]
        except Exception as e:
            print(f"加载预算失败: {e}")

    def save(self):
        """保存预算信息
        
        Returns:
            bool: 保存是否成功
        """
        try:
            if self.budget_id:
                # 更新现有预算
                db_manager.execute_query(
                    "UPDATE budgets SET amount = ? WHERE budget_id = ?",
                    (self.amount, self.budget_id),
                    commit=True
                )
            else:
                # 创建新预算
                self.budget_id = str(uuid.uuid4())
                db_manager.execute_query(
                    '''INSERT OR REPLACE INTO budgets 
                    (budget_id, user_id, month, amount, spent) 
                    VALUES (?, ?, ?, ?, ?)''',
                    (self.budget_id, self.user_id, self.month, self.amount, self.spent),
                    commit=True
                )
            
            return True
        except Exception as e:
            print(f"保存预算失败: {e}")
            return False

    def update_spent(self):
        """更新已花费金额
        
        Returns:
            bool: 更新是否成功
        """
        try:
            # 计算该月总支出
            total_spent = db_manager.execute_query(
                '''SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE user_id = ? AND type = '支出' AND date LIKE ?''',
                (self.user_id, f"{self.month}%"),
            )[0][0]
            
            self.spent = total_spent
            
            # 更新数据库
            if self.budget_id:
                db_manager.execute_query(
                    "UPDATE budgets SET spent = ? WHERE budget_id = ?",
                    (total_spent, self.budget_id),
                    commit=True
                )
            else:
                # 检查是否存在该月预算
                budget_data = db_manager.execute_query(
                    "SELECT budget_id FROM budgets WHERE user_id = ? AND month = ?",
                    (self.user_id, self.month)
                )
                
                if budget_data:
                    self.budget_id = budget_data[0][0]
                    db_manager.execute_query(
                        "UPDATE budgets SET spent = ? WHERE budget_id = ?",
                        (total_spent, self.budget_id),
                        commit=True
                    )
                else:
                    # 从数据库直接获取用户默认预算
                    user_data = db_manager.execute_query(
                        "SELECT monthly_budget FROM users WHERE user_id = ?",
                        (self.user_id,)
                    )
                    if user_data:
                        self.amount = user_data[0][0]
                        self.budget_id = str(uuid.uuid4())
                        db_manager.execute_query(
                            '''INSERT INTO budgets 
                            (budget_id, user_id, month, amount, spent) 
                            VALUES (?, ?, ?, ?, ?)''',
                            (self.budget_id, self.user_id, self.month, self.amount, total_spent),
                            commit=True
                        )
            
            return True
        except Exception as e:
            print(f"更新预算支出失败: {e}")
            return False

    def is_overspent(self):
        """检查是否超支
        
        Returns:
            bool: 是否超支
        """
        # 确保已更新支出金额
        self.update_spent()
        return self.spent > self.amount

    @staticmethod
    def get_monthly_budget(user_id, month):
        """获取指定月份的预算
        
        Args:
            user_id: 用户ID
            month: 月份，格式为'YYYY-MM'
        
        Returns:
            Budget: 预算对象
        """
        return Budget(user_id=user_id, month=month)

    @staticmethod
    def get_all_budgets(user_id):
        """获取用户所有预算
        
        Args:
            user_id: 用户ID
        
        Returns:
            list: 预算对象列表
        """
        try:
            budgets_data = db_manager.execute_query(
                "SELECT budget_id, month, amount, spent FROM budgets WHERE user_id = ? ORDER BY month DESC",
                (user_id,)
            )
            
            budgets = []
            for data in budgets_data:
                budget = Budget(
                    budget_id=data[0],
                    user_id=user_id,
                    month=data[1],
                    amount=data[2],
                    spent=data[3]
                )
                budgets.append(budget)
            
            return budgets
        except Exception as e:
            print(f"获取预算列表失败: {e}")
            return []

    def get_remaining(self):
        """获取剩余预算
        
        Returns:
            float: 剩余金额
        """
        return self.amount - self.spent

    def get_spent_percentage(self):
        """获取已花费百分比
        
        Returns:
            float: 百分比值（0-100）
        """
        if self.amount <= 0:
            return 0
        return (self.spent / self.amount) * 100