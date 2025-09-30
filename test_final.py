import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.clickhouse_client import ClickHouseClient


def test_final():
    print("🎯 FINAL CLICKHOUSE TEST")

    try:
        # Пробуем основную конфигурацию
        print("1. Testing primary configuration...")
        ch = ClickHouseClient(use_alt_config=False)
        version = ch.execute("SELECT version()")[0][0]
        print(f"   ✅ Primary config works! Version: {version}")
        return True

    except Exception as e:
        print(f"   ❌ Primary config failed: {e}")

        try:
            # Пробуем альтернативную конфигурацию
            print("2. Testing alternative configuration...")
            ch = ClickHouseClient(use_alt_config=True)
            version = ch.execute("SELECT version()")[0][0]
            print(f"   ✅ Alternative config works! Version: {version}")
            return True

        except Exception as e2:
            print(f"   ❌ Alternative config failed: {e2}")
            return False


if __name__ == "__main__":
    success = test_final()
    if success:
        print("\n🎉 CLICKHOUSE IS FULLY OPERATIONAL!")
    else:
        print("\n💥 CLICKHOUSE SETUP NEEDS ATTENTION!")