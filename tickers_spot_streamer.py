import sys
import os
from datetime import datetime
from time import sleep
import requests
from pybit.unified_trading import WebSocket

# Добавляем корневую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from utils.clickhouse_client import ClickHouseClient


class SpotTickerStreamer:
    def __init__(self):
        self.ch_client = ClickHouseClient()
        self.ws = None
        self.setup_tables()

    def setup_tables(self):
        """Создаем таблицу для spot тикеров если не существует"""
        table_schema = """
            `event_time` DateTime64(3),
            `receive_time` DateTime64(3),
            `insert_time` DateTime64(3) DEFAULT now64(),
            `symbol` String,
            `tick_direction` String,
            `last_price` Float64,
            `prev_price_24h` Float64,
            `price_24h_pcnt` Float64,
            `high_price_24h` Float64,
            `low_price_24h` Float64,
            `prev_price_1h` Float64,
            `mark_price` Float64,
            `index_price` Float64,
            `turnover_24h` Float64,
            `volume_24h` Float64,
            `bid1_price` Float64,
            `bid1_size` Float64,
            `ask1_price` Float64,
            `ask1_size` Float64,
            INDEX idx_symbol_event (symbol, event_time) TYPE minmax GRANULARITY 3
        """
        self.ch_client.create_table("bybit_tickers_spot", table_schema)
        print("✅ Spot tickers table ready")

    def handle_spot_ticker(self, message):
        """Обработчик spot тикеров"""
        try:
            data = message.get('data', {})
            if not data:
                return

            # Временные метки
            event_time = datetime.fromtimestamp(int(data.get('ts', 0)) / 1000) if data.get('ts') else datetime.now()
            receive_time = datetime.now()

            # Подготовка данных для вставки
            record = (
                event_time,
                receive_time,
                data.get('symbol'),
                data.get('tickDirection', ''),
                float(data.get('lastPrice', 0)),
                float(data.get('prevPrice24h', 0)),
                float(data.get('price24hPcnt', 0)),
                float(data.get('highPrice24h', 0)),
                float(data.get('lowPrice24h', 0)),
                float(data.get('prevPrice1h', 0)),
                float(data.get('markPrice', 0)),
                float(data.get('indexPrice', 0)),
                float(data.get('turnover24h', 0)),
                float(data.get('volume24h', 0)),
                float(data.get('bid1Price', 0)),
                float(data.get('bid1Size', 0)),
                float(data.get('ask1Price', 0)),
                float(data.get('ask1Size', 0))
            )

            # Вставка в ClickHouse
            self.ch_client.insert_data("bybit_tickers_spot", [record])
            print(f"📊 Spot: {data.get('symbol')} - {data.get('lastPrice')}")

        except Exception as e:
            print(f"❌ Error processing spot ticker: {e}")

    def get_spot_symbols(self):
        """Получение списка всех spot пар USDT"""
        url = "https://api.bybit.com/v5/market/instruments-info"
        try:
            response = requests.get(url, params={'category': 'spot'})
            data = response.json().get('result', {}).get('list', [])
            symbols = [s['symbol'] for s in data
                       if s.get('quoteCoin') == 'USDT'
                       and s.get('status') == 'Trading']
            print(f"✅ Found {len(symbols)} spot trading pairs")
            return symbols
        except Exception as e:
            print(f"❌ Error fetching spot symbols: {e}")
            return []

    def subscribe_all_spot(self):
        """Подписка на все spot пары с лимитом 10 символов за раз"""
        symbols = self.get_spot_symbols()
        if not symbols:
            print("❌ No symbols found for subscription")
            return

        args_limit = 10
        for i in range(0, len(symbols), args_limit):
            chunk = symbols[i:i + args_limit]
            try:
                # Используем правильный метод ticker_stream для spot
                self.ws.ticker_stream(
                    symbol=chunk,
                    callback=self.handle_spot_ticker
                )
                print(f"✅ Subscribed to {len(chunk)} spot symbols: {chunk}")
                sleep(0.5)  # Задержка между подписками
            except Exception as e:
                print(f"❌ Error subscribing to {chunk}: {e}")

    def start_streaming(self):
        """Запуск стриминга spot тикеров"""
        print("🚀 Starting spot ticker streamer...")

        self.ws = WebSocket(
            testnet=False,
            channel_type="spot"
        )

        # Подписка на все пары
        self.subscribe_all_spot()

        # Бесконечный цикл для поддержания соединения
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            print("⏹️ Stopping spot ticker streamer...")
        except Exception as e:
            print(f"❌ Spot streamer error: {e}")


def main():
    streamer = SpotTickerStreamer()
    streamer.start_streaming()


if __name__ == '__main__':
    main()