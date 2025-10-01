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
        try:
            self.ch_client.execute("DROP TABLE IF EXISTS bybit_tickers_linear")
            print("🗑️ Old linear table dropped")
        except Exception as e:
            print(f"ℹ️ No existing linear table to drop: {e}")

        # Создаем таблицу с правильной структурой (22 колонки)
        create_table_sql = """
        CREATE TABLE bybit_tickers_linear
        (
            `event_time` DateTime64(3),
            `receive_time` DateTime64(3),
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
            `next_funding_time` Nullable(DateTime64(3)),
            `bid1_price` Float64,
            `bid1_size` Float64,
            `ask1_price` Float64,
            `ask1_size` Float64,
            INDEX idx_symbol_event (symbol, event_time) TYPE minmax GRANULARITY 3
        )
        ENGINE = MergeTree
        PARTITION BY toYYYYMMDD(event_time)
        ORDER BY (symbol, event_time)
        SETTINGS index_granularity = 8192;
        """
        self.ch_client.execute(create_table_sql)
        print("✅ Linear tickers table created successfully")

    def safe_float(self, value, default=0.0):
        """Безопасное преобразование в float"""
        if value is None or value == '':
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def safe_timestamp(self, ts_value):
        """Безопасное преобразование timestamp"""
        if not ts_value:
            return datetime.now()
        try:
            return datetime.fromtimestamp(int(ts_value) / 1000)
        except (ValueError, TypeError):
            return datetime.now()

    def safe_datetime(self, dt_value):
        """Безопасное преобразование datetime с обработкой None"""
        if not dt_value or dt_value == '':
            return None
        try:
            return datetime.fromtimestamp(int(dt_value) / 1000)
        except (ValueError, TypeError):
            return None

    def handle_linear_ticker(self, message):
        """Обработчик linear тикеров"""
        try:
            data = message.get('data', {})
            if not data:
                return

            # Временные метки
            event_time = self.safe_timestamp(data.get('ts'))
            receive_time = datetime.now()

            # Обработка next_funding_time - безопасная обработка None
            next_funding_time = self.safe_datetime(data.get('nextFundingTime'))

            # Подготовка данных для вставки - 22 значения для 22 колонок
            record = (
                event_time,  # event_time
                receive_time,  # receive_time
                data.get('symbol', ''),  # symbol
                data.get('tickDirection', ''),  # tick_direction
                self.safe_float(data.get('lastPrice')),  # last_price
                self.safe_float(data.get('prevPrice24h')),  # prev_price_24h
                self.safe_float(data.get('price24hPcnt')),  # price_24h_pcnt
                self.safe_float(data.get('highPrice24h')),  # high_price_24h
                self.safe_float(data.get('lowPrice24h')),  # low_price_24h
                self.safe_float(data.get('prevPrice1h')),  # prev_price_1h
                self.safe_float(data.get('markPrice')),  # mark_price
                self.safe_float(data.get('indexPrice')),  # index_price
                self.safe_float(data.get('openInterest')),  # open_interest
                self.safe_float(data.get('openInterestValue')),  # open_interest_value
                self.safe_float(data.get('turnover24h')),  # turnover_24h
                self.safe_float(data.get('volume24h')),  # volume_24h
                self.safe_float(data.get('fundingRate')),  # funding_rate
                next_funding_time,  # next_funding_time (может быть None)
                self.safe_float(data.get('bid1Price')),  # bid1_price
                self.safe_float(data.get('bid1Size')),  # bid1_size
                self.safe_float(data.get('ask1Price')),  # ask1_price
                self.safe_float(data.get('ask1Size'))  # ask1_size
            )

            # Проверяем длину записи
            if len(record) != 22:
                print(f"⚠️ Warning: Record length is {len(record)}, expected 22")
                return

            # Вставка в ClickHouse без указания колонок
            self.ch_client.insert_data("bybit_tickers_linear", [record])
            print(f"📊 Linear: {data.get('symbol')} - {data.get('lastPrice')}")

        except Exception as e:
            print(f"❌ Error processing linear ticker: {e}")
            print(f"   Data: {data}")

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