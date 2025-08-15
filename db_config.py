import mysql.connector
from config import MYSQL_CONFIG

def get_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)
