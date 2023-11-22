import asyncio
import websockets
import ssl
import configparser
import mysql.connector
from mysql.connector import Error
from register_user import register_user  # Import the register_user function from register_user.py


# Function to load configuration
def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    registration = config.getboolean('Settings', 'Registration')
    db_config = config['Database']
    ssl_config = config['SSL']
    server_config = config['Server']
    messages = config['Messages']
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

# Function to handle user registration removed to register_user.py


# Websocket server handler
async def server_handler(websocket, path):
    registration, db_config, ssl_config, server_config, messages = load_config()
    greeting_key = 'greeting_with_registration' if registration else 'greeting_without_registration'
    greeting_message = messages[greeting_key]
    await websocket.send(greeting_message)

    try:
        while True:
            message = await websocket.recv()
            if message.lower() == "login":
                login_success = await check_credentials(websocket, db_config)
                await websocket.send("Login successful." if login_success else "Login failed.")
            elif message.lower() == "register" and registration:
                await register_user(websocket, db_config)
            else:
                await websocket.send("Unknown command. Try 'login' or 'register'.")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed.")


# Start the websocket server
async def start_server():
    _, _, ssl_config, server_config, _ = load_config()
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(ssl_config['certfile'], ssl_config['keyfile'])
    async with websockets.serve(server_handler, server_config['host'], int(server_config['port']), ssl=ssl_context):
        await asyncio.Future()

# Run the server
asyncio.run(start_server())
