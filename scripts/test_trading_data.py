import sys
import os
from datetime import datetime

# Добавляем корневую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from utils.clickhouse_client import ClickHouseClient


def test_trading_data():
    """Тестируем запись реальных торговых данных"""
    ch = ClickHouseClient()

    # Тестовые сделки
    trades_data = [
        (datetime.now(), 'BTCUSDT', 'buy', 50000.0, 0.1, 'trade_001', 'mean_reversion'),
        (datetime.now(), 'ETHUSDT', 'sell', 3500.0, 1.0, 'trade_002', 'momentum'),
        (datetime.now(), 'BTCUSDT', 'sell', 51000.0, 0.05, 'trade_003', 'mean_reversion')
    ]

    ch.insert_data("trades", trades_data)
    print("✅ Test trades inserted")

    # Тестовые ордера
    orders_data = [
        (datetime.now(), 'BTCUSDT', 'limit', 'buy', 49500.0, 0.1, 'filled', 'order_001', 'mean_reversion'),
        (datetime.now(), 'ETHUSDT', 'market', 'sell', 0.0, 1.0, 'filled', 'order_002', 'momentum')
    ]

    ch.insert_data("orders", orders_data)
    print("✅ Test orders inserted")

    # Проверяем что данные записались
    trades_count = ch.execute("SELECT COUNT(*) FROM trades")[0][0]
    orders_count = ch.execute("SELECT COUNT(*) FROM orders")[0][0]

    print(f"✅ Total trades: {trades_count}")
    print(f"✅ Total orders: {orders_count}")

    # Показываем последние сделки
    recent_trades = ch.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 3")
    print("✅ Recent trades:")
    for trade in recent_trades:
        print(f"   {trade}")


if __name__ == "__main__":
    test_trading_data()