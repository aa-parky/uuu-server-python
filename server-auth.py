import asyncio
import websockets
import ssl
import configparser
import mysql.connector
from mysql.connector import Error
import datetime

# Function to load configuration
def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    registration = config.getboolean('Settings', 'Registration')
    db_config = config['Database']
    ssl_config = config['SSL']
    server_config = config['Server']
    messages = config['Messages']  # Load messages from config.ini
    return registration, db_config, ssl_config, server_config, messages

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

# Function to log connection attempts
def log_connection(attempted, username, success, reason):
    now = datetime.datetime.now()
    log_message = f"{now}: {attempted} connection attempt by username '{username}' - {'Successful' if success else 'Failed'} - Reason: {reason}"
    with open("connection_log.txt", "a") as log_file:
        log_file.write(log_message + "\n")

# Function to check user credentials
async def check_user_credentials(username, password, db_config):
    connection = create_db_connection(db_config)
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT password FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            record = cursor.fetchone()
            cursor.close()
            connection.close()
            if record and password == record[0]:
                return True, "Login successful"
            else:
                return False, "Invalid username or password"
        except Error as e:
            return False, f"Error: {e}"
    else:
        return False, "Database connection error"

# Echo function with registration logic
async def handle_client(websocket, path, registration_enabled, db_config, messages):
    greeting_message = messages['greeting_with_registration'] if registration_enabled else messages['greeting_without_registration']
    await websocket.send(greeting_message)

    async for message in websocket:
        print(f"Received message: {message}")
        parts = message.split()
        attempted = "Unknown"
        if parts[0].lower() == "login":
            attempted = "Login"
            if len(parts) == 3:
                username, password = parts[1], parts[2]
                success, reason = await check_user_credentials(username, password, db_config)
                await websocket.send(reason)
                log_connection(attempted, username, success, reason)
        elif registration_enabled and parts[0].lower() == "register":
            attempted = "Registration"
            # Add registration logic here

async def main():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    registration_enabled, db_config, ssl_config, server_config, messages = load_config()
    ssl_context.load_cert_chain(certfile=ssl_config['certfile'], keyfile=ssl_config['keyfile'])
    server_host = server_config['host']
    server_port = int(server_config['port'])

    async with websockets.serve(lambda ws, path: handle_client(ws, path, registration_enabled, db_config, messages),
                                server_host, server_port, ssl=ssl_context):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
