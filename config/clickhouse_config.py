import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

CLICKHOUSE_CONFIG = {
    'host': os.getenv('CLICKHOUSE_HOST'),
    'port': int(os.getenv('CLICKHOUSE_PORT', 9440)),
    'user': os.getenv('CLICKHOUSE_USER'),
    'password': os.getenv('CLICKHOUSE_PASSWORD'),
    'database': os.getenv('CLICKHOUSE_DB'),
    'secure': True,
    'verify': True,
    'ca_certs': '/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt'
}