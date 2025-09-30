import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.clickhouse_client import ClickHouseClient


def test_connection():
    try:
        ch = ClickHouseClient()
        result = ch.execute("SELECT version()")
        print(f"✅ ClickHouse version: {result[0][0]}")

        # Test data insertion
        test_data = [('2024-01-01 10:00:00', 'BTCUSDT', 'buy', 50000.0, 0.1, 'test_1', 'test_strategy')]
        ch.insert_data("trades", test_data)
        print("✅ Test data inserted successfully")

        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()