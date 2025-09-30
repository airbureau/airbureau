import sys
import os

# Добавляем корневую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.clickhouse_client import ClickHouseClient


def analyze_trading_data():
    ch = ClickHouseClient()

    print("📊 TRADING DATA ANALYSIS")
    print("=" * 50)

    # Общая статистика
    total_trades = ch.execute("SELECT COUNT(*) FROM trades")[0][0]
    total_orders = ch.execute("SELECT COUNT(*) FROM orders")[0][0]

    print(f"Total trades: {total_trades}")
    print(f"Total orders: {total_orders}")

    if total_trades > 0:
        # Статистика по стратегиям
        print("\n📈 Strategy Performance:")
        strategy_stats = ch.execute("""
            SELECT 
                strategy,
                COUNT(*) as trade_count,
                SUM(CASE WHEN side = 'buy' THEN quantity * price ELSE 0 END) as buy_volume,
                SUM(CASE WHEN side = 'sell' THEN quantity * price ELSE 0 END) as sell_volume,
                AVG(price) as avg_price
            FROM trades 
            GROUP BY strategy
        """)

        for strategy, count, buy_vol, sell_vol, avg_price in strategy_stats:
            print(f"  {strategy}:")
            print(f"    Trades: {count}")
            print(f"    Buy Volume: ${buy_vol:.2f}")
            print(f"    Sell Volume: ${sell_vol:.2f}")
            print(f"    Avg Price: ${avg_price:.2f}")

        # Последние сделки
        print("\n🕒 Recent Trades:")
        recent_trades = ch.execute("""
            SELECT timestamp, symbol, side, price, quantity, strategy 
            FROM trades 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)

        for trade in recent_trades:
            timestamp, symbol, side, price, quantity, strategy = trade
            print(f"  {timestamp} | {symbol} | {side} | ${price} | {quantity} | {strategy}")

    else:
        print("No trading data found. Run test trading data first.")


if __name__ == "__main__":
    analyze_trading_data()