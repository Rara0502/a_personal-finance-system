#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计分析模块
实现统计相关的业务逻辑和图表生成
"""
from datetime import datetime, timedelta
from collections import defaultdict
from database import db_manager
from category import Category


class Statistics:
    """统计类，负责数据统计和分析"""

    def __init__(self, user_id):
        """初始化统计对象
        
        Args:
            user_id: 用户ID
        """
        self.user_id = user_id
        self.total_income = 0
        self.total_expense = 0
        self.balance = 0

    def calculate_daily_stats(self, date=None):
        """计算日统计数据
        
        Args:
            date: 日期，格式为'YYYY-MM-DD'，默认为今天
        
        Returns:
            dict: 统计结果
        """
        try:
            # 如果没有指定日期，使用今天
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            # 查询收入
            income_result = db_manager.execute_query(
                '''SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE user_id = ? AND type = '收入' AND date LIKE ?''',
                (self.user_id, f"{date}%"),
            )
            self.total_income = income_result[0][0]
            
            # 查询支出
            expense_result = db_manager.execute_query(
                '''SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE user_id = ? AND type = '支出' AND date LIKE ?''',
                (self.user_id, f"{date}%"),
            )
            self.total_expense = expense_result[0][0]
            
            # 计算余额
            self.balance = self.total_income - self.total_expense
            
            # 获取分类统计
            category_stats = self._get_category_stats(date)
            
            return {
                'date': date,
                'total_income': self.total_income,
                'total_expense': self.total_expense,
                'balance': self.balance,
                'category_stats': category_stats
            }
        except Exception as e:
            print(f"计算日统计失败: {e}")
            return None

    def calculate_monthly_stats(self, month=None):
        """计算月统计数据
        
        Args:
            month: 月份，格式为'YYYY-MM'，默认为当前月
        
        Returns:
            dict: 统计结果
        """
        try:
            # 如果没有指定月份，使用当前月
            if not month:
                month = datetime.now().strftime('%Y-%m')
            
            # 查询收入
            income_result = db_manager.execute_query(
                '''SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE user_id = ? AND type = '收入' AND date LIKE ?''',
                (self.user_id, f"{month}%"),
            )
            self.total_income = income_result[0][0]
            
            # 查询支出
            expense_result = db_manager.execute_query(
                '''SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE user_id = ? AND type = '支出' AND date LIKE ?''',
                (self.user_id, f"{month}%"),
            )
            self.total_expense = expense_result[0][0]
            
            # 计算余额
            self.balance = self.total_income - self.total_expense
            
            # 获取每日统计
            daily_stats = self._get_daily_stats_by_month(month)
            
            # 获取分类统计
            category_stats = self._get_category_stats_by_month(month)
            
            return {
                'month': month,
                'total_income': self.total_income,
                'total_expense': self.total_expense,
                'balance': self.balance,
                'daily_stats': daily_stats,
                'category_stats': category_stats
            }
        except Exception as e:
            print(f"计算月统计失败: {e}")
            return None

    def calculate_yearly_stats(self, year=None):
        """计算年统计数据
        
        Args:
            year: 年份，格式为'YYYY'，默认为当前年
        
        Returns:
            dict: 统计结果
        """
        try:
            # 如果没有指定年份，使用当前年
            if not year:
                year = datetime.now().strftime('%Y')
            
            # 查询收入
            income_result = db_manager.execute_query(
                '''SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE user_id = ? AND type = '收入' AND date LIKE ?''',
                (self.user_id, f"{year}%"),
            )
            self.total_income = income_result[0][0]
            
            # 查询支出
            expense_result = db_manager.execute_query(
                '''SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE user_id = ? AND type = '支出' AND date LIKE ?''',
                (self.user_id, f"{year}%"),
            )
            self.total_expense = expense_result[0][0]
            
            # 计算余额
            self.balance = self.total_income - self.total_expense
            
            # 获取月度统计
            monthly_stats = self._get_monthly_stats_by_year(year)
            
            # 获取分类统计
            category_stats = self._get_category_stats_by_year(year)
            
            return {
                'year': year,
                'total_income': self.total_income,
                'total_expense': self.total_expense,
                'balance': self.balance,
                'monthly_stats': monthly_stats,
                'category_stats': category_stats
            }
        except Exception as e:
            print(f"计算年统计失败: {e}")
            return None

    def _get_category_stats(self, date):
        """获取指定日期的分类统计"""
        try:
            # 查询分类支出统计
            expense_data = db_manager.execute_query(
                '''SELECT c.category_id, c.name, c.icon, SUM(t.amount) 
                FROM transactions t 
                JOIN categories c ON t.category_id = c.category_id 
                WHERE t.user_id = ? AND t.type = '支出' AND t.date LIKE ? 
                GROUP BY c.category_id, c.name, c.icon 
                ORDER BY SUM(t.amount) DESC''',
                (self.user_id, f"{date}%"),
            )
            
            # 查询分类收入统计
            income_data = db_manager.execute_query(
                '''SELECT c.category_id, c.name, c.icon, SUM(t.amount) 
                FROM transactions t 
                JOIN categories c ON t.category_id = c.category_id 
                WHERE t.user_id = ? AND t.type = '收入' AND t.date LIKE ? 
                GROUP BY c.category_id, c.name, c.icon 
                ORDER BY SUM(t.amount) DESC''',
                (self.user_id, f"{date}%"),
            )
            
            return {
                'expense': [{'category_id': d[0], 'name': d[1], 'icon': d[2], 'amount': d[3]} for d in expense_data],
                'income': [{'category_id': d[0], 'name': d[1], 'icon': d[2], 'amount': d[3]} for d in income_data]
            }
        except Exception as e:
            print(f"获取分类统计失败: {e}")
            return {'expense': [], 'income': []}

    def _get_category_stats_by_month(self, month):
        """获取指定月份的分类统计"""
        try:
            # 查询分类支出统计
            expense_data = db_manager.execute_query(
                '''SELECT c.category_id, c.name, c.icon, SUM(t.amount) 
                FROM transactions t 
                JOIN categories c ON t.category_id = c.category_id 
                WHERE t.user_id = ? AND t.type = '支出' AND t.date LIKE ? 
                GROUP BY c.category_id, c.name, c.icon 
                ORDER BY SUM(t.amount) DESC''',
                (self.user_id, f"{month}%"),
            )
            
            # 查询分类收入统计
            income_data = db_manager.execute_query(
                '''SELECT c.category_id, c.name, c.icon, SUM(t.amount) 
                FROM transactions t 
                JOIN categories c ON t.category_id = c.category_id 
                WHERE t.user_id = ? AND t.type = '收入' AND t.date LIKE ? 
                GROUP BY c.category_id, c.name, c.icon 
                ORDER BY SUM(t.amount) DESC''',
                (self.user_id, f"{month}%"),
            )
            
            return {
                'expense': [{'category_id': d[0], 'name': d[1], 'icon': d[2], 'amount': d[3]} for d in expense_data],
                'income': [{'category_id': d[0], 'name': d[1], 'icon': d[2], 'amount': d[3]} for d in income_data]
            }
        except Exception as e:
            print(f"获取月度分类统计失败: {e}")
            return {'expense': [], 'income': []}

    def _get_category_stats_by_year(self, year):
        """获取指定年份的分类统计"""
        try:
            # 查询分类支出统计
            expense_data = db_manager.execute_query(
                '''SELECT c.category_id, c.name, c.icon, SUM(t.amount) 
                FROM transactions t 
                JOIN categories c ON t.category_id = c.category_id 
                WHERE t.user_id = ? AND t.type = '支出' AND t.date LIKE ? 
                GROUP BY c.category_id, c.name, c.icon 
                ORDER BY SUM(t.amount) DESC''',
                (self.user_id, f"{year}%"),
            )
            
            # 查询分类收入统计
            income_data = db_manager.execute_query(
                '''SELECT c.category_id, c.name, c.icon, SUM(t.amount) 
                FROM transactions t 
                JOIN categories c ON t.category_id = c.category_id 
                WHERE t.user_id = ? AND t.type = '收入' AND t.date LIKE ? 
                GROUP BY c.category_id, c.name, c.icon 
                ORDER BY SUM(t.amount) DESC''',
                (self.user_id, f"{year}%"),
            )
            
            return {
                'expense': [{'category_id': d[0], 'name': d[1], 'icon': d[2], 'amount': d[3]} for d in expense_data],
                'income': [{'category_id': d[0], 'name': d[1], 'icon': d[2], 'amount': d[3]} for d in income_data]
            }
        except Exception as e:
            print(f"获取年度分类统计失败: {e}")
            return {'expense': [], 'income': []}

    def _get_daily_stats_by_month(self, month):
        """获取指定月份的每日统计"""
        try:
            # 查询每日收入和支出
            daily_data = db_manager.execute_query(
                '''SELECT SUBSTR(date, 1, 10) as day, type, SUM(amount) 
                FROM transactions 
                WHERE user_id = ? AND date LIKE ? 
                GROUP BY day, type 
                ORDER BY day''',
                (self.user_id, f"{month}%"),
            )
            
            # 整理数据
            daily_dict = defaultdict(lambda: {'income': 0, 'expense': 0})
            for data in daily_data:
                day = data[0]
                trans_type = data[1]
                amount = data[2]
                
                if trans_type == '收入':
                    daily_dict[day]['income'] = amount
                else:
                    daily_dict[day]['expense'] = amount
            
            # 转换为列表并按日期排序
            daily_list = [{'date': day, **stats} for day, stats in sorted(daily_dict.items())]
            
            return daily_list
        except Exception as e:
            print(f"获取每日统计失败: {e}")
            return []

    def _get_monthly_stats_by_year(self, year):
        """获取指定年份的月度统计"""
        try:
            # 查询月度收入和支出
            monthly_data = db_manager.execute_query(
                '''SELECT SUBSTR(date, 1, 7) as month, type, SUM(amount) 
                FROM transactions 
                WHERE user_id = ? AND date LIKE ? 
                GROUP BY month, type 
                ORDER BY month''',
                (self.user_id, f"{year}%"),
            )
            
            # 整理数据
            monthly_dict = defaultdict(lambda: {'income': 0, 'expense': 0})
            for data in monthly_data:
                month = data[0]
                trans_type = data[1]
                amount = data[2]
                
                if trans_type == '收入':
                    monthly_dict[month]['income'] = amount
                else:
                    monthly_dict[month]['expense'] = amount
            
            # 转换为列表并按月份排序
            monthly_list = [{'month': month, **stats} for month, stats in sorted(monthly_dict.items())]
            
            return monthly_list
        except Exception as e:
            print(f"获取月度统计失败: {e}")
            return []

    def generate_charts(self, chart_type='monthly', period=None):
        """生成统计图表数据
        
        Args:
            chart_type: 图表类型 ('daily', 'monthly', 'yearly')
            period: 统计周期
        
        Returns:
            dict: 图表数据
        """
        try:
            if chart_type == 'daily':
                stats = self.calculate_daily_stats(period)
                if not stats:
                    return None
                
                # 生成饼图数据
                category_expense = [
                    {'name': item['name'], 'value': item['amount']} 
                    for item in stats['category_stats']['expense']
                ]
                
                return {
                    'pie_chart': category_expense,
                    'bar_chart': {
                        'labels': ['收入', '支出'],
                        'datasets': [{
                            'data': [stats['total_income'], stats['total_expense']],
                            'backgroundColor': ['#4CAF50', '#F44336']
                        }]
                    }
                }
            
            elif chart_type == 'monthly':
                stats = self.calculate_monthly_stats(period)
                if not stats:
                    return None
                
                # 生成折线图数据（每日收支）
                labels = [item['date'].split('-')[2] for item in stats['daily_stats']]
                income_data = [item['income'] for item in stats['daily_stats']]
                expense_data = [item['expense'] for item in stats['daily_stats']]
                
                # 生成饼图数据（分类支出）
                category_expense = [
                    {'name': item['name'], 'value': item['amount']} 
                    for item in stats['category_stats']['expense']
                ]
                
                return {
                    'line_chart': {
                        'labels': labels,
                        'datasets': [
                            {
                                'label': '收入',
                                'data': income_data,
                                'borderColor': '#4CAF50',
                                'fill': False
                            },
                            {
                                'label': '支出',
                                'data': expense_data,
                                'borderColor': '#F44336',
                                'fill': False
                            }
                        ]
                    },
                    'pie_chart': category_expense
                }
            
            elif chart_type == 'yearly':
                stats = self.calculate_yearly_stats(period)
                if not stats:
                    return None
                
                # 生成柱状图数据（每月收支）
                labels = [item['month'].split('-')[1] for item in stats['monthly_stats']]
                income_data = [item['income'] for item in stats['monthly_stats']]
                expense_data = [item['expense'] for item in stats['monthly_stats']]
                
                # 生成饼图数据（分类支出）
                category_expense = [
                    {'name': item['name'], 'value': item['amount']} 
                    for item in stats['category_stats']['expense']
                ]
                
                return {
                    'bar_chart': {
                        'labels': labels,
                        'datasets': [
                            {
                                'label': '收入',
                                'data': income_data,
                                'backgroundColor': '#4CAF50'
                            },
                            {
                                'label': '支出',
                                'data': expense_data,
                                'backgroundColor': '#F44336'
                            }
                        ]
                    },
                    'pie_chart': category_expense
                }
            
            return None
        except Exception as e:
            print(f"生成图表数据失败: {e}")
            return None

    def get_trends(self, months=6):
        """获取收支趋势
        
        Args:
            months: 统计月数
        
        Returns:
            dict: 趋势数据
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months*30)
            
            trends_data = db_manager.execute_query(
                '''SELECT SUBSTR(date, 1, 7) as month, type, SUM(amount) 
                FROM transactions 
                WHERE user_id = ? AND date >= ? 
                GROUP BY month, type 
                ORDER BY month''',
                (self.user_id, start_date.strftime('%Y-%m-%d')),
            )
            
            # 整理数据
            monthly_dict = defaultdict(lambda: {'income': 0, 'expense': 0})
            for data in trends_data:
                month = data[0]
                trans_type = data[1]
                amount = data[2]
                
                if trans_type == '收入':
                    monthly_dict[month]['income'] = amount
                else:
                    monthly_dict[month]['expense'] = amount
            
            # 生成完整的月份列表
            current = start_date
            while current <= end_date:
                month_str = current.strftime('%Y-%m')
                if month_str not in monthly_dict:
                    monthly_dict[month_str] = {'income': 0, 'expense': 0}
                current += timedelta(days=32)
                current = current.replace(day=1)
            
            # 转换为列表并按月份排序
            trend_list = [{'month': month, **stats} for month, stats in sorted(monthly_dict.items())]
            
            return trend_list
        except Exception as e:
            print(f"获取趋势数据失败: {e}")
            return []