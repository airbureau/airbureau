import sys
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.clickhouse_client import ClickHouseClient


def test_connection():
    try:
        # Сначала проверим переменные окружения
        required_vars = ['CLICKHOUSE_HOST', 'CLICKHOUSE_USER', 'CLICKHOUSE_PASSWORD', 'CLICKHOUSE_DB']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            print("💡 Make sure .env file exists and contains all required variables")
            return False

        print("✅ Environment variables found")
        print(f"   Host: {os.getenv('CLICKHOUSE_HOST')}")
        print(f"   User: {os.getenv('CLICKHOUSE_USER')}")
        print(f"   Database: {os.getenv('CLICKHOUSE_DB')}")
        print(f"   Port: {os.getenv('CLICKHOUSE_PORT', 9440)}")

        # Тестируем подключение
        print("🔄 Testing ClickHouse connection...")
        ch = ClickHouseClient()
        result = ch.execute("SELECT version()")
        print(f"✅ ClickHouse version: {result[0][0]}")

        # Дополнительный тест - создание тестовой таблицы
        print("🔄 Testing table creation...")
        test_table_schema = """
            id Int32,
            test_string String,
            created_at DateTime DEFAULT now()
        """
        ch.create_table("test_connection", test_table_schema)

        # Тест вставки данных
        print("🔄 Testing data insertion...")
        test_data = [(1, 'test_value_1'), (2, 'test_value_2')]
        ch.insert_data("test_connection", test_data)

        # Тест чтения данных
        print("🔄 Testing data reading...")
        result = ch.execute("SELECT COUNT(*) FROM test_connection")
        print(f"✅ Test table contains {result[0][0]} rows")

        # Очистка тестовой таблицы
        ch.execute("DROP TABLE IF EXISTS test_connection")
        print("✅ Cleanup completed")

        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_connection()