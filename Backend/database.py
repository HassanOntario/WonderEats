import pymysql
from pymysql.cursors import DictCursor
import os
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'hassanismael'),
    'password': os.getenv('DB_PASSWORD', 'Hassan123!'),
    'database': os.getenv('DB_NAME', 'GardenOfEaten'),
    'cursorclass': DictCursor
}

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    connection = pymysql.connect(**DB_CONFIG)
    try:
        yield connection
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()

def get_db_cursor(connection):
    """Get a cursor from a connection"""
    return connection.cursor()
