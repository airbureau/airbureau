from clickhouse_driver import Client
from config.clickhouse_config import CLICKHOUSE_CONFIG, CLICKHOUSE_CONFIG_ALT
import logging

logger = logging.getLogger(__name__)


class ClickHouseClient:
    def __init__(self, use_alt_config=False):
        self.client = None
        self.use_alt_config = use_alt_config
        self.connect()

    def connect(self):
        config = CLICKHOUSE_CONFIG_ALT if self.use_alt_config else CLICKHOUSE_CONFIG

        try:
            logger.info(f"Connecting to ClickHouse (alt config: {self.use_alt_config})")
            self.client = Client(**config)

            # Проверяем подключение
            self.client.execute('SELECT 1')
            logger.info("✅ Successfully connected to ClickHouse")

        except Exception as e:
            logger.error(f"❌ Primary connection failed: {e}")

            # Пробуем альтернативную конфигурацию
            if not self.use_alt_config:
                logger.info("🔄 Trying alternative configuration...")
                self.use_alt_config = True
                self.connect()
            else:
                raise

    def execute(self, query, params=None):
        try:
            return self.client.execute(query, params)
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise

    def insert_data(self, table, data):
        if not data:
            return
        self.client.execute(f"INSERT INTO {table} VALUES", data)
        logger.info(f"Inserted {len(data)} rows into {table}")

    def create_table(self, table_name, schema):
        self.client.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema}) ENGINE = MergeTree() ORDER BY tuple()")
        logger.info(f"Table {table_name} created or already exists")