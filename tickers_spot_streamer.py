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

    def handle_spot_ticker(self, message):
        """Обработчик spot тикеров"""
        try:
            data = message.get('data', {})
            if not data:
                return

            # Временные метки
            event_time = self.safe_timestamp(data.get('ts'))
            receive_time = datetime.now()

            # Подготовка данных для вставки - теперь 18 значений для 18 колонок (insert_time имеет DEFAULT)
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
                self.safe_float(data.get('turnover24h')),  # turnover_24h
                self.safe_float(data.get('volume24h')),  # volume_24h
                self.safe_float(data.get('bid1Price')),  # bid1_price
                self.safe_float(data.get('bid1Size')),  # bid1_size
                self.safe_float(data.get('ask1Price')),  # ask1_price
                self.safe_float(data.get('ask1Size'))  # ask1_size
                # insert_time пропускаем - будет DEFAULT now64()
            )

            # Вставка в ClickHouse
            self.ch_client.insert_data("bybit_tickers_spot", [record])
            # print(f"📊 Spot: {data.get('symbol')} - {data.get('lastPrice')}")

        except Exception as e:
            print(f"❌ Error processing spot ticker: {e}")
            print(f"   Data: {data}")

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
                self.ws.ticker_stream(
                    symbol=chunk,
                    callback=self.handle_spot_ticker
                )
                print(f"✅ Subscribed to {len(chunk)} spot symbols: {chunk}")
                sleep(0.5)
            except Exception as e:
                print(f"❌ Error subscribing to {chunk}: {e}")

    def start_streaming(self):
        """Запуск стриминга spot тикеров"""
        print("🚀 Starting spot ticker streamer...")

        self.ws = WebSocket(
            testnet=False,
            channel_type="spot"
        )

        self.subscribe_all_spot()

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