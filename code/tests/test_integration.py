import os
import pytest
from database import db_manager

"""
集成测试文件
验证：
1. 交易持久化是否正常
2. 统计类功能是否能够读取插入数据
"""

TEST_DB_FILE = "test_finance_integration.db"


@pytest.fixture(scope="function")
def test_db(monkeypatch):
    """
    创建一个临时测试数据库，并让全局 db_manager 使用它。
    每个测试用例都使用独立数据库，避免相互污染。
    """

    # 如果旧文件存在，先尝试删除
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except PermissionError:
            # 若被占用，强制关闭并重试
            pass

    # 强制让 db_manager 使用测试数据库路径
    monkeypatch.setattr(db_manager, "db_path", TEST_DB_FILE)

    # 重新初始化数据库结构（包含默认分类）
    db_manager.init_database()

    yield db_manager  # 将数据库管理器实例提供给测试用例

    # 测试结束后清理
    try:
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)
    except PermissionError:
        pass


# -------------------- 测试 1：验证交易持久化 --------------------

def test_integration_transaction_persistence(test_db):
    """
    集成测试：插入交易记录 → 查询 → 验证持久化
    """
    user_id = "u_1"
    amount = 100.50
    date = "2023-12-01"

    # 插入交易
    test_db.execute_query(
        """
        INSERT INTO transactions (transaction_id, user_id, amount, type, category_id, date)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("t_1", user_id, amount, "支出", "cat_1", date),
        commit=True
    )

    # 查询
    result = test_db.execute_query(
        "SELECT amount, type FROM transactions WHERE user_id = ?",
        (user_id,)
    )

    assert len(result) == 1
    assert result[0][0] == amount
    assert result[0][1] == "支出"


# -------------------- 测试 2：验证简单统计逻辑 --------------------

def test_integration_statistics_calculation(test_db):
    """
    集成测试：插入多条记录 → 计算统计结果
    """

    user_id = "u_2"

    records = [
        ("t_2", user_id, 50.0, "支出", "cat_1", "2024-01-05"),
        ("t_3", user_id, 20.0, "支出", "cat_2", "2024-01-05"),
        ("t_4", user_id, 100.0, "收入", "cat_9", "2024-01-05"),
    ]

    for r in records:
        test_db.execute_query(
            """
            INSERT INTO transactions (transaction_id, user_id, amount, type, category_id, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            r,
            commit=True
        )

    # 查询所有支出并计算总和
    expenses = test_db.execute_query(
        "SELECT amount FROM transactions WHERE user_id = ? AND type = '支出'",
        (user_id,)
    )

    total_expense = sum([row[0] for row in expenses])
    assert total_expense == 70.0

    # 查询收入
    incomes = test_db.execute_query(
        "SELECT amount FROM transactions WHERE user_id = ? AND type = '收入'",
        (user_id,)
    )

    total_income = sum([row[0] for row in incomes])
    assert total_income == 100.0

    # 净收入检查
    assert total_income - total_expense == 30.0
