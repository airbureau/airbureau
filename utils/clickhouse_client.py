from clickhouse_driver import Client
from config.clickhouse_config import CLICKHOUSE_CONFIG
import logging

logger = logging.getLogger(__name__)


class ClickHouseClient:
    def __init__(self):
        self.client = None
        self.connect()

    def connect(self):
        try:
            self.client = Client(**CLICKHOUSE_CONFIG)
            logger.info("✅ Successfully connected to ClickHouse")
        except Exception as e:
            logger.error(f"❌ Failed to connect to ClickHouse: {e}")
            raise

    def execute(self, query, params=None):
        try:
            return self.client.execute(query, params)
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            raise

    def insert_data(self, table, data):
        if not data:
            return
        try:
            self.client.execute(f"INSERT INTO {table} VALUES", data)
            logger.info(f"✅ Inserted {len(data)} rows into {table}")
        except Exception as e:
            logger.error(f"❌ Failed to insert data into {table}: {e}")
            raise

    def create_table(self, table_name, schema):
        try:
            self.client.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} ({schema}) ENGINE = MergeTree() ORDER BY tuple()")
            logger.info(f"✅ Table {table_name} created or already exists")
        except Exception as e:
            logger.error(f"❌ Failed to create table {table_name}: {e}")
            raise