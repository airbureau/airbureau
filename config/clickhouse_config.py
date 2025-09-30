import os

CLICKHOUSE_CONFIG = {
    'host': os.getenv('CLICKHOUSE_HOST', 'your-host.mdb.yandexcloud.net'),
    'port': int(os.getenv('CLICKHOUSE_PORT', 9440)),
    'user': os.getenv('CLICKHOUSE_USER', 'your-username'),
    'password': os.getenv('CLICKHOUSE_PASSWORD', 'your-password'),
    'database': os.getenv('CLICKHOUSE_DB', 'your-database'),
    'secure': True,
    'verify': True
}