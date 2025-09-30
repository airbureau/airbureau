import sys
import os

# Добавляем корневую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from utils.clickhouse_client import ClickHouseClient


def create_trading_tables():
    ch = ClickHouseClient()

    tables = {
        "trades": """
            timestamp DateTime,
            symbol String,
            side String,
            price Float64,
            quantity Float64,
            trade_id String,
            strategy String
        """,
        "orders": """
            timestamp DateTime,
            symbol String,
            order_type String,
            side String,
            price Float64,
            quantity Float64,
            status String,
            order_id String,
            strategy String
        """,
        "market_data": """
            timestamp DateTime,
            symbol String,
            open Float64,
            high Float64,
            low Float64,
            close Float64,
            volume Float64,
            timeframe String
        """,
        "strategy_metrics": """
            timestamp DateTime,
            strategy String,
            pnl Float64,
            drawdown Float64,
            sharpe_ratio Float64,
            total_trades Int32,
            winning_trades Int32
        """
    }

    for table_name, schema in tables.items():
        ch.create_table(table_name, schema)

    print("✅ All trading tables created successfully!")


if __name__ == "__main__":
    create_trading_tables()