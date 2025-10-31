#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易记录模块
实现交易相关的业务逻辑
"""
import uuid
from datetime import datetime
from database import db_manager
from budget import Budget


class Transaction:
    """交易记录类，负责交易信息管理"""

    def __init__(self, transaction_id=None, amount=None, type=None, category_id=None,
                 date=None, note=None, user_id=None):
        """初始化交易对象"""
        self.transaction_id = transaction_id
        self.amount = amount
        self.type = type  # 收入/支出
        self.category_id = category_id
        self.date = date
        self.note = note
        self.user_id = user_id

    def add_transaction(self):
        """添加交易记录
        
        Returns:
            bool: 添加是否成功
        """
        try:
            # 生成交易ID
            self.transaction_id = str(uuid.uuid4())
            
            # 确保日期格式
            if isinstance(self.date, datetime):
                self.date = self.date.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(self.date, str):
                # 尝试解析常见日期格式
                try:
                    # 尝试多种日期格式
                    formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%d %H:%M']
                    for fmt in formats:
                        try:
                            parsed_date = datetime.strptime(self.date, fmt)
                            self.date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                            break
                        except ValueError:
                            continue
                except:
                    # 如果解析失败，使用当前时间
                    self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 插入交易数据
            db_manager.execute_query(
                '''INSERT INTO transactions 
                (transaction_id, amount, type, category_id, date, note, user_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (self.transaction_id, self.amount, self.type, self.category_id,
                 self.date, self.note, self.user_id),
                commit=True
            )
            
            # 如果是支出，更新预算
            if self.type == '支出':
                # 提取月份
                month = self.date.split('-')[0] + '-' + self.date.split('-')[1]
                # 更新预算支出
                budget = Budget(user_id=self.user_id, month=month)
                budget.update_spent()
            
            return True
        except Exception as e:
            print(f"添加交易记录失败: {e}")
            return False

    def edit_transaction(self):
        """编辑交易记录
        
        Returns:
            bool: 编辑是否成功
        """
        try:
            # 获取原交易记录以更新预算
            old_transaction = Transaction.get_transaction_by_id(self.transaction_id)
            old_month = None
            if old_transaction and old_transaction.type == '支出':
                old_month = old_transaction.date.split('-')[0] + '-' + old_transaction.date.split('-')[1]
            
            # 更新交易记录
            db_manager.execute_query(
                '''UPDATE transactions 
                SET amount = ?, type = ?, category_id = ?, date = ?, note = ? 
                WHERE transaction_id = ? AND user_id = ?''',
                (self.amount, self.type, self.category_id, self.date,
                 self.note, self.transaction_id, self.user_id),
                commit=True
            )
            
            # 更新预算
            # 1. 如果原记录是支出，更新原月份预算
            if old_month:
                budget = Budget(user_id=self.user_id, month=old_month)
                budget.update_spent()
            
            # 2. 如果新记录是支出，更新新月份预算
            if self.type == '支出':
                new_month = self.date.split('-')[0] + '-' + self.date.split('-')[1]
                if new_month != old_month:
                    budget = Budget(user_id=self.user_id, month=new_month)
                    budget.update_spent()
            
            return True
        except Exception as e:
            print(f"编辑交易记录失败: {e}")
            return False

    def delete_transaction(self):
        """删除交易记录
        
        Returns:
            bool: 删除是否成功
        """
        try:
            # 获取交易记录以更新预算
            transaction = Transaction.get_transaction_by_id(self.transaction_id)
            month = None
            if transaction and transaction.type == '支出':
                month = transaction.date.split('-')[0] + '-' + transaction.date.split('-')[1]
            
            # 删除交易记录
            db_manager.execute_query(
                "DELETE FROM transactions WHERE transaction_id = ? AND user_id = ?",
                (self.transaction_id, self.user_id),
                commit=True
            )
            
            # 更新预算
            if month:
                budget = Budget(user_id=self.user_id, month=month)
                budget.update_spent()
            
            return True
        except Exception as e:
            print(f"删除交易记录失败: {e}")
            return False

    @staticmethod
    def get_transactions_by_user(user_id, start_date=None, end_date=None, transaction_type=None,
                                category_id=None, min_amount=None, max_amount=None):
        """根据条件查询交易记录
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            transaction_type: 交易类型
            category_id: 分类ID
            min_amount: 最小金额
            max_amount: 最大金额
        
        Returns:
            list: 交易记录列表
        """
        try:
            # 构建查询条件
            query = "SELECT * FROM transactions WHERE user_id = ?"
            params = [user_id]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            
            if transaction_type:
                query += " AND type = ?"
                params.append(transaction_type)
            
            if category_id:
                query += " AND category_id = ?"
                params.append(category_id)
            
            if min_amount is not None:
                query += " AND amount >= ?"
                params.append(min_amount)
            
            if max_amount is not None:
                query += " AND amount <= ?"
                params.append(max_amount)
            
            query += " ORDER BY date DESC"
            
            transactions_data = db_manager.execute_query(query, params)
            
            transactions = []
            for data in transactions_data:
                transaction = Transaction(
                    transaction_id=data[0],
                    amount=data[1],
                    type=data[2],
                    category_id=data[3],
                    date=data[4],
                    note=data[5],
                    user_id=data[6]
                )
                transactions.append(transaction)
            
            return transactions
        except Exception as e:
            print(f"查询交易记录失败: {e}")
            return []

    @staticmethod
    def get_transaction_by_id(transaction_id):
        """根据ID获取交易记录
        
        Args:
            transaction_id: 交易记录ID
        
        Returns:
            Transaction: 交易记录对象
        """
        try:
            transaction_data = db_manager.execute_query(
                "SELECT * FROM transactions WHERE transaction_id = ?",
                (transaction_id,)
            )
            
            if not transaction_data:
                return None
            
            data = transaction_data[0]
            return Transaction(
                transaction_id=data[0],
                amount=data[1],
                type=data[2],
                category_id=data[3],
                date=data[4],
                note=data[5],
                user_id=data[6]
            )
        except Exception as e:
            print(f"获取交易记录失败: {e}")
            return None


class SearchCriteria:
    """搜索条件类"""

    def __init__(self, start_date=None, end_date=None, category=None,
                 min_amount=None, max_amount=None):
        """初始化搜索条件"""
        self.start_date = start_date
        self.end_date = end_date
        self.category = category  # 这里可以是分类对象或分类ID
        self.min_amount = min_amount
        self.max_amount = max_amount

    def search(self, user_id):
        """执行搜索
        
        Args:
            user_id: 用户ID
        
        Returns:
            list: 交易记录列表
        """
        category_id = self.category.category_id if hasattr(self.category, 'category_id') else self.category
        
        return Transaction.get_transactions_by_user(
            user_id=user_id,
            start_date=self.start_date,
            end_date=self.end_date,
            category_id=category_id,
            min_amount=self.min_amount,
            max_amount=self.max_amount
        )