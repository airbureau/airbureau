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


class LinearTickerStreamer:
    def __init__(self):
        self.ch_client = ClickHouseClient()
        self.ws = None
        self.setup_tables()

    def setup_tables(self):
        """Создаем таблицу для linear тикеров если не существует"""
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
            `open_interest` Float64,
            `open_interest_value` Float64,
            `turnover_24h` Float64,
            `volume_24h` Float64,
            `funding_rate` Float64,
            `next_funding_time` DateTime64(3),
            `bid1_price` Float64,
            `bid1_size` Float64,
            `ask1_price` Float64,
            `ask1_size` Float64,
            INDEX idx_symbol_event (symbol, event_time) TYPE minmax GRANULARITY 3
        """
        self.ch_client.create_table("bybit_tickers_linear", table_schema)
        print("✅ Linear tickers table ready")

    def handle_linear_ticker(self, message):
        """Обработчик linear тикеров"""
        try:
            data = message.get('data', {})
            if not data:
                return

            # Временные метки
            event_time = datetime.fromtimestamp(int(data.get('ts', 0)) / 1000) if data.get('ts') else datetime.now()
            receive_time = datetime.now()

            # Обработка next_funding_time
            next_funding_time = None
            if data.get('nextFundingTime'):
                try:
                    next_funding_time = datetime.fromtimestamp(int(data['nextFundingTime']) / 1000)
                except:
                    next_funding_time = None

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
                float(data.get('openInterest', 0)),
                float(data.get('openInterestValue', 0)),
                float(data.get('turnover24h', 0)),
                float(data.get('volume24h', 0)),
                float(data.get('fundingRate', 0)),
                next_funding_time,
                float(data.get('bid1Price', 0)),
                float(data.get('bid1Size', 0)),
                float(data.get('ask1Price', 0)),
                float(data.get('ask1Size', 0))
            )

            # Вставка в ClickHouse
            self.ch_client.insert_data("bybit_tickers_linear", [record])
            print(f"📊 Linear: {data.get('symbol')} - {data.get('lastPrice')}")

        except Exception as e:
            print(f"❌ Error processing linear ticker: {e}")

    def get_linear_symbols(self):
        """Получение списка всех linear пар USDT"""
        url = "https://api.bybit.com/v5/market/instruments-info"
        try:
            response = requests.get(url, params={'category': 'linear'})
            data = response.json().get('result', {}).get('list', [])
            symbols = [s['symbol'] for s in data
                       if s.get('quoteCoin') == 'USDT'
                       and s.get('status') == 'Trading']
            print(f"✅ Found {len(symbols)} linear trading pairs")
            return symbols
        except Exception as e:
            print(f"❌ Error fetching linear symbols: {e}")
            return []

    def subscribe_all_linear(self):
        """Подписка на все linear пары с учетом лимита длины строки"""
        symbols = self.get_linear_symbols()
        if not symbols:
            print("❌ No symbols found for subscription")
            return

        # Группировка символов с учетом лимита длины строки (21000 символов)
        max_length = 21000
        current_group = []
        current_length = 0

        for symbol in symbols:
            symbol_length = len(symbol) + 1  # +1 для запятой

            if current_length + symbol_length > max_length and current_group:
                # Подписываемся на текущую группу
                self.subscribe_to_group(current_group)
                current_group = []
                current_length = 0

            current_group.append(symbol)
            current_length += symbol_length

        # Подписываемся на оставшиеся символы
        if current_group:
            self.subscribe_to_group(current_group)

    def subscribe_to_group(self, symbols):
        """Подписка на группу символов"""
        try:
            # Используем правильный метод ticker_stream для linear
            self.ws.ticker_stream(
                symbol=symbols,
                callback=self.handle_linear_ticker
            )
            print(f"✅ Subscribed to {len(symbols)} linear symbols")
            sleep(0.3)  # Задержка между подписками
        except Exception as e:
            print(f"❌ Error subscribing to linear group: {e}")

    def start_streaming(self):
        """Запуск стриминга linear тикеров"""
        print("🚀 Starting linear ticker streamer...")

        self.ws = WebSocket(
            testnet=False,
            channel_type="linear"
        )

        # Подписка на все пары
        self.subscribe_all_linear()

        # Бесконечный цикл для поддержания соединения
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            print("⏹️ Stopping linear ticker streamer...")
        except Exception as e:
            print(f"❌ Linear streamer error: {e}")


def main():
    streamer = LinearTickerStreamer()
    streamer.start_streaming()


if __name__ == '__main__':
    main()