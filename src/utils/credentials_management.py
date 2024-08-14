import os
from dotenv import load_dotenv

load_dotenv()


def get_database_credentials():

    return {
        'dbname': os.getenv('DBNAME'),
        'user': os.getenv('DBUSER'),
        'password': os.getenv('DBPASS'),
        'host': os.getenv('DBHOST'),
        'port': os.getenv('DBPORT')
    }
