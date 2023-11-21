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


# Websocket server handler
async def server_handler(websocket, path):
    # Load config
    registration, db_config, ssl_config, server_config, messages = load_config()

    # Choose the right greeting message
    greeting_message = messages['greeting_with_registration'] if registration else messages[
        'greeting_without_registration']

    # Send the greeting message to the client
    await websocket.send(greeting_message)

    # Here you can add more interaction logic with the client if needed


# Start the websocket server
async def start_server():
    # Load config
    _, _, ssl_config, server_config, _ = load_config()

    # Setup SSL context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(ssl_config['certfile'], ssl_config['keyfile'])

    # Start the server
    async with websockets.serve(server_handler, server_config['host'], int(server_config['port']), ssl=ssl_context):
        await asyncio.Future()  # Run the server until it's manually stopped


# Run the server
asyncio.run(start_server())
