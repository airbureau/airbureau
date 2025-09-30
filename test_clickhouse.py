import sys
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.clickhouse_client import ClickHouseClient


def test_connection():
    try:
        print("🔄 Testing ClickHouse connection...")

        # Тестируем подключение
        ch = ClickHouseClient()

        # Проверяем версию
        result = ch.execute("SELECT version()")
        print(f"✅ ClickHouse version: {result[0][0]}")

        # Проверяем текущую базу данных
        result = ch.execute("SELECT currentDatabase()")
        print(f"✅ Current database: {result[0][0]}")

        # Простой тест создания таблицы и вставки данных
        print("🔄 Testing basic operations...")

        # Создаем временную таблицу с 2 колонками для теста
        ch.create_table("test_temp", """
            id Int32,
            name String
        """)

        # Вставляем тестовые данные (2 значения - id и name)
        test_data = [
            (1, 'test_1'),
            (2, 'test_2'),
            (3, 'test_3')
        ]
        ch.insert_data("test_temp", test_data)

        # Проверяем что данные вставились
        result = ch.execute("SELECT COUNT(*) FROM test_temp")
        print(f"✅ Test table contains {result[0][0]} rows")

        # Читаем данные
        result = ch.execute("SELECT * FROM test_temp ORDER BY id")
        print("✅ Test data:")
        for row in result:
            print(f"   {row}")

        # Убираем за собой
        ch.execute("DROP TABLE test_temp")
        print("✅ Cleanup completed")

        print("🎉 ALL TESTS PASSED! ClickHouse integration is working!")
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_connection()