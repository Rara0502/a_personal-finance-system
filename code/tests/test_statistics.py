import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# 1. 路径设置
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from finance_stats import Statistics


class TestStatistics:
    """
    综合增强版测试用例，覆盖统计模块主要逻辑。
    """

    def setup_method(self):
        self.user_id = 1
        self.stats = Statistics(self.user_id)

    # ============================================================
    # 1. 日统计 calculate_daily_stats
    # ============================================================

    @patch('finance_stats.db_manager')
    def test_calculate_daily_stats_success(self, mock_db):
        mock_db.execute_query.side_effect = [
            [(1000,)],
            [(200,)],
            [(1, 'Food', 'icon', 200)],
            [(2, 'Salary', 'icon', 1000)]
        ]

        result = self.stats.calculate_daily_stats('2023-12-01')

        assert result['total_income'] == 1000
        assert result['total_expense'] == 200
        assert result['balance'] == 800
        assert result['category_stats']['expense'][0]['name'] == 'Food'

    @patch('finance_stats.db_manager')
    def test_calculate_daily_stats_default_date(self, mock_db):
        mock_db.execute_query.side_effect = [
            [(0,)], [(0,)], [], []
        ]

        self.stats.calculate_daily_stats()
        today = datetime.now().strftime('%Y-%m-%d')

        args, _ = mock_db.execute_query.call_args_list[0]
        assert today in args[1][1]

    @patch('finance_stats.db_manager.execute_query', side_effect=Exception("DB"))
    def test_calculate_daily_stats_exception(self, mock_db):
        result = self.stats.calculate_daily_stats("2023-12-01")
        assert result is None

    # ============================================================
    # 2. 月统计 calculate_monthly_stats
    # ============================================================

    @patch('finance_stats.db_manager')
    def test_calculate_monthly_stats_success(self, mock_db):
        mock_db.execute_query.side_effect = [
            [(5000,)],
            [(3000,)],
            [('2023-12-01', '收入', 5000), ('2023-12-02', '支出', 1000)],
            [(1, 'Food', 'icon', 3000)],
            [(2, 'Salary', 'icon', 5000)]
        ]

        res = self.stats.calculate_monthly_stats("2023-12")
        assert res['balance'] == 2000
        assert res['daily_stats'][0]['income'] == 5000

    @patch('finance_stats.db_manager.execute_query', side_effect=Exception("DB"))
    def test_calculate_monthly_stats_exception(self, mock_db):
        result = self.stats.calculate_monthly_stats("2023-12")
        assert result is None

    # ============================================================
    # 3. 年统计 calculate_yearly_stats（新增完整测试）
    # ============================================================

    @patch('finance_stats.db_manager')
    def test_calculate_yearly_stats_success(self, mock_db):
        mock_db.execute_query.side_effect = [
            [(10000,)],                      # 年收入
            [(5000,)],                       # 年支出
            [('2023-01', '收入', 2000)],     # monthly stats
            [(1, "Food", "icon", 5000)],     # expense
            [(2, "Salary", "icon", 10000)]   # income
        ]

        res = self.stats.calculate_yearly_stats('2023')
        assert res['balance'] == 5000
        assert len(res['monthly_stats']) == 1

    @patch('finance_stats.db_manager.execute_query', side_effect=Exception("DB Lost"))
    def test_calculate_yearly_stats_exception(self, mock_db):
        assert self.stats.calculate_yearly_stats("2023") is None

    # ============================================================
    # 4. 私有函数 _get_category_stats / _get_daily_stats_by_month 等
    # ============================================================

    @patch('finance_stats.db_manager.execute_query', side_effect=Exception("DB"))
    def test_get_category_stats_exception(self, mock_db):
        res = self.stats._get_category_stats("2023-12-01")
        assert res == {'expense': [], 'income': []}

    @patch('finance_stats.db_manager.execute_query', side_effect=Exception("DB"))
    def test_get_category_stats_by_month_exception(self, mock_db):
        res = self.stats._get_category_stats_by_month("2023-12")
        assert res == {'expense': [], 'income': []}

    @patch('finance_stats.db_manager.execute_query', side_effect=Exception("DB"))
    def test_get_category_stats_by_year_exception(self, mock_db):
        res = self.stats._get_category_stats_by_year("2023")
        assert res == {'expense': [], 'income': []}

    @patch('finance_stats.db_manager.execute_query', side_effect=Exception("DB"))
    def test_get_daily_stats_by_month_exception(self, mock_db):
        assert self.stats._get_daily_stats_by_month("2023-12") == []

    @patch('finance_stats.db_manager.execute_query', side_effect=Exception("DB"))
    def test_get_monthly_stats_by_year_exception(self, mock_db):
        assert self.stats._get_monthly_stats_by_year("2023") == []

    # ============================================================
    # 5. generate_charts
    # ============================================================

    def test_generate_charts_daily(self):
        mock_data = {
            'date': '2023-12-01',
            'total_income': 100,
            'total_expense': 50,
            'balance': 50,
            'category_stats': {
                'expense': [{'name': 'Food', 'amount': 50}],
                'income': []
            }
        }

        with patch.object(self.stats, 'calculate_daily_stats', return_value=mock_data):
            charts = self.stats.generate_charts('daily', '2023-12-01')
            assert charts['pie_chart'][0]['value'] == 50

    def test_generate_charts_monthly(self):
        mock_data = {
            'month': '2023-12',
            'total_income': 200,
            'total_expense': 100,
            'balance': 100,
            'daily_stats': [
                {'date': '2023-12-01', 'income': 200, 'expense': 0},
                {'date': '2023-12-02', 'income': 0, 'expense': 100}
            ],
            'category_stats': {
                'expense': [{'name': 'Food', 'amount': 100}],
                'income': []
            }
        }

        with patch.object(self.stats, 'calculate_monthly_stats', return_value=mock_data):
            charts = self.stats.generate_charts('monthly', '2023-12')
            assert charts['line_chart']['labels'] == ['01', '02']

    # 新增 yearly 图表测试
    def test_generate_charts_yearly(self):
        mock_data = {
            'year': '2023',
            'monthly_stats': [
                {'month': '2023-01', 'income': 500, 'expense': 100},
                {'month': '2023-02', 'income': 300, 'expense': 200}
            ],
            'category_stats': {'expense': [], 'income': []}
        }

        with patch.object(self.stats, 'calculate_yearly_stats', return_value=mock_data):
            result = self.stats.generate_charts('yearly', '2023')
            assert 'bar_chart' in result

    # generate_charts - stats 返回 None
    def test_generate_charts_stats_none(self):
        with patch.object(self.stats, 'calculate_daily_stats', return_value=None):
            assert self.stats.generate_charts('daily') is None

    # generate_charts - 无效类型
    def test_generate_charts_invalid_type(self):
        assert self.stats.generate_charts("invalid", "2023") is None

    # ============================================================
    # 6. get_trends（已有，但增强）
    # ============================================================

    @patch('finance_stats.db_manager')
    def test_get_trends(self, mock_db):
        mock_db.execute_query.return_value = [
            ('2023-10', '收入', 1000),
            ('2023-12', '支出', 500)
        ]

        trends = self.stats.get_trends(months=3)
        assert isinstance(trends, list)
        assert any(item['month'] == '2023-10' for item in trends)

    @patch('finance_stats.db_manager.execute_query', side_effect=Exception("DB"))
    def test_get_trends_exception(self, mock_db):
        assert self.stats.get_trends(3) == []
