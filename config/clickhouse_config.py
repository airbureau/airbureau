import os
from dotenv import load_dotenv

load_dotenv()

# Основная конфигурация
CLICKHOUSE_CONFIG = {
    'host': os.getenv('CLICKHOUSE_HOST'),
    'port': 9440,
    'user': os.getenv('CLICKHOUSE_USER'),
    'password': os.getenv('CLICKHOUSE_PASSWORD'),
    'database': os.getenv('CLICKHOUSE_DB'),
    'secure': True,
    'verify': True,
    'ca_certs': '/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt',
    'settings': {
        'use_numpy': False,
        'connect_timeout': 10,
        'send_receive_timeout': 30,
    }
}

# Альтернативная конфигурация (если основная не работает)
CLICKHOUSE_CONFIG_ALT = {
    'host': os.getenv('CLICKHOUSE_HOST'),
    'port': 9440,
    'user': os.getenv('CLICKHOUSE_USER'),
    'password': os.getenv('CLICKHOUSE_PASSWORD'),
    'database': os.getenv('CLICKHOUSE_DB'),
    'secure': True,
    'verify': False,  # Без проверки SSL
    'settings': {
        'use_numpy': False,
        'connect_timeout': 10,
    }
}