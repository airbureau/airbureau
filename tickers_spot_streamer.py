import asyncio
import json
import time
from datetime import datetime

from clickhouse_connect import get_client
from pybit import usdt_perpetual

# ClickHouse клиент
client = get_client(
    host='localhost',
    port=8123,
    username='user',
    password='pass',
    database='db1'
)

# WebSocket Bybit spot-тикеры
session = usdt_perpetual.WebSocket(
    test=False,
    subscriptions=['ticker'],
    subscriptions_filter={'symbol': []},
)

# Колонки согласно таблице без insert_time
COLUMNS = [
    'event_time', 'receive_time', 'symbol', 'tick_direction',
    'last_price', 'prev_price_24h', 'price_24h_pcnt',
    'high_price_24h', 'low_price_24h', 'prev_price_1h',
    'mark_price', 'index_price', 'turnover_24h',
    'volume_24h', 'bid1_price', 'bid1_size',
    'ask1_price', 'ask1_size'
]

async def process_ticker(msg):
    data = msg.get('data', {})
    # Приводим к нужным типам
    record = {
        'event_time': datetime.fromtimestamp(msg['timestamp'] / 1000),
        'receive_time': datetime.now(),
        'symbol': data.get('symbol', ''),
        'tick_direction': data.get('tickDirection', ''),
        'last_price': float(data.get('lastPrice', 0)),
        'prev_price_24h': float(data.get('prevPrice24h', 0)),
        'price_24h_pcnt': float(data.get('price24hPcnt', 0)),
        'high_price_24h': float(data.get('highPrice24h', 0)),
        'low_price_24h': float(data.get('lowPrice24h', 0)),
        'prev_price_1h': float(data.get('prevPrice1h', 0)),
        'mark_price': float(data.get('markPrice', 0)),
        'index_price': float(data.get('usdIndexPrice', 0)),
        'turnover_24h': float(data.get('turnover24h', 0)),
        'volume_24h': float(data.get('volume24h', 0)),
        'bid1_price': float(data.get('bid1Price', 0)),
        'bid1_size': float(data.get('bid1Size', 0)),
        'ask1_price': float(data.get('ask1Price', 0)),
        'ask1_size': float(data.get('ask1Size', 0)),
    }

    # Проверяем, что все ключи на месте
    if set(record.keys()) != set(COLUMNS):
        print(f"❌ Неверный набор полей: ожидалось {len(COLUMNS)}, получено {len(record)}")
        return

    # Составляем данные для вставки
    row = [record[col] for col in COLUMNS]

    # Вставляем в ClickHouse; insert_time заполнится автоматически
    try:
        client.insert(
            table='bybit_tickers_spot',
            columns=COLUMNS,
            data=[row]
        )
        print(f"✅ Inserted {record['symbol']} at {record['receive_time']}")
    except Exception as e:
        print(f"❌ Error inserting {record['symbol']}: {e}")

async def main():
    session.run_forever(process_ticker)

if __name__ == '__main__':
    asyncio.run(main())
