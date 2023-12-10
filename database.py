import mysql.connector
from mysql.connector import Error


def create_db_connection(db_config):
    try:
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            port=db_config.get('port', 3306)
        )
        return connection
    except Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return None
