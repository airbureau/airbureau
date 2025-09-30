import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.clickhouse_client import ClickHouseClient


def test_connection():
    try:
        # Сначала проверим переменные окружения
        required_vars = ['CLICKHOUSE_HOST', 'CLICKHOUSE_USER', 'CLICKHOUSE_PASSWORD', 'CLICKHOUSE_DB']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            return False

        print("✅ Environment variables found")

        # Тестируем подключение
        ch = ClickHouseClient()
        result = ch.execute("SELECT version()")
        print(f"✅ ClickHouse version: {result[0][0]}")
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()