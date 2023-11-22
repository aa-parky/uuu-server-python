import mysql.connector
from mysql.connector import Error


# Function to create a database connection
def create_db_connection(db_config):
    try:
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        return connection
    except Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return None


# Function to check user credentials
async def check_credentials(websocket, db_config):
    await websocket.send("Enter username:")
    username = await websocket.recv()
    await websocket.send("Enter password:")
    password = await websocket.recv()

    connection = create_db_connection(db_config)
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            user_password = cursor.fetchone()
            cursor.close()
            connection.close()
            return user_password and user_password[0] == password
        except Error as e:
            print(f"Database error: {e}")
            return False
    else:
        return False