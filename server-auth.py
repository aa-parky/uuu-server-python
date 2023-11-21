import asyncio
import websockets
import ssl
import configparser
import mysql.connector
from mysql.connector import Error
import datetime  # Import the datetime module for logging

# Function to load configuration
def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config.getboolean('Settings', 'Registration'), config['Database']

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
            if record and password == record[0]:  # Simplified for demonstration, use hashed password comparison
                return True, "Login successful"
            else:
                return False, "Invalid username or password"
        except Error as e:
            return False, f"Error: {e}"
    else:
        return False, "Database connection error"

# Echo function with registration logic
async def handle_client(websocket, path, registration_enabled, db_config):
    greeting_message = "Sparkfuse Signals here! Login with [login]"
    if registration_enabled:
        greeting_message += " or Register with [register]"
    else:
        greeting_message += ". Registration currently closed"

    await websocket.send(greeting_message)

    async for message in websocket:
        # Parse the message and perform actions based on the content.
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
    ssl_context.load_cert_chain(certfile="C:/MAMP/bin/certs/uuu-websocket-test.cert",
                                keyfile="C:/MAMP/bin/certs/uuu-websocket-test.key")

    registration_enabled, db_config = load_config()

    async with websockets.serve(lambda ws, path: handle_client(ws, path, registration_enabled, db_config), "localhost", 7450, ssl=ssl_context):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
