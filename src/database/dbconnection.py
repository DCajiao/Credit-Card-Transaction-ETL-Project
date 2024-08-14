import psycopg2
import logging

from utils.credentials_management import get_database_credentials

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


class DB:
    def __init__(self):
        credentials = get_database_credentials()
        self.dbname = credentials['dbname']
        self.user = credentials['user']
        self.password = credentials['password']
        self.host = credentials['host']
        self.port = credentials['port']
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor()
            logging.info("- Connected to database")
        except Exception as e:
            logging.error(f"Error connecting to database: {e}")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
            logging.info("- Cursor closed")
        if self.conn:
            logging.info("- Connection closed")
            self.conn.close()

    def execute(self, query):
        try:
            self.cursor.execute(query)
            logging.info("- Query executed")
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            raise
