#!/usr/bin/env python3
"""
Главный скрипт для управления торговым ботом и утилитами
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()


def main():
    print("🤖 AirBureau Trading Bot Management")
    print("=" * 40)
    print("1. Test ClickHouse connection")
    print("2. Create trading tables")
    print("3. Insert test trading data")
    print("4. Run trading bot")
    print("5. Analyze trading data")
    print("0. Exit")

    choice = input("\nSelect option: ").strip()

    if choice == "1":
        from test_clickhouse import test_connection
        test_connection()
    elif choice == "2":
        from scripts.create_tables import create_trading_tables
        create_trading_tables()
    elif choice == "3":
        from scripts.test_trading_data import test_trading_data
        test_trading_data()
    elif choice == "4":
        print("🚀 Starting trading bot...")
        # Здесь будет запуск вашего основного бота
        # from bot.main import main as bot_main
        # bot_main()
        print("Trading bot started (not implemented yet)")
    elif choice == "5":
        from scripts.analyze_data import analyze_trading_data
        analyze_trading_data()
    elif choice == "0":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid option")


if __name__ == "__main__":
    main()