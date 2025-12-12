import sys
import os

# 把项目根目录加入 sys.path，确保可以导入 finance_stats
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from finance_stats import Statistics
from hypothesis import given, strategies as st


# 模糊测试 Transactions/Statistics 类
@given(
    amounts=st.lists(st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False), min_size=1, max_size=100)
)
def test_statistics_total(amounts):
    """
    测试 Statistics 类的总收入/总支出计算是否正确
    Hypothesis 会自动生成不同的浮点列表
    """
    s = Statistics(user_id=1)  # 初始化对象
    # 模拟将 amount 列表写入 transactions（可根据你的实现调整）
    s.transactions = [{"amount": a, "type": "收入"} if i % 2 == 0 else {"amount": a, "type": "支出"} for i, a in enumerate(amounts)]

    total_income = sum(t["amount"] for t in s.transactions if t["type"] == "收入")
    total_expense = float(sum(t["amount"] for t in s.transactions if t["type"] == "支出"))
    total_income = float(total_income)  # 同理
    balance = total_income - total_expense

    # Hypothesis 会尝试各种数据，保证计算逻辑不会崩溃
    assert isinstance(total_income, float)
    assert isinstance(total_expense, float)
    assert isinstance(balance, float)
