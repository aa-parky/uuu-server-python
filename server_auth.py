import asyncio
import websockets
import ssl
import configparser
import random
import string
import mysql.connector
from mysql.connector import Error

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


# Function to handle user registration
async def register_user(websocket, db_config):
    await websocket.send("Enter email address for registration:")
    email = await websocket.recv()

    connection = create_db_connection(db_config)
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
            existing_email = cursor.fetchone()
            cursor.close()

            if existing_email:
                await websocket.send("Email already exists. Did you forget your password?")
                return False
            else:
                await websocket.send("Enter a username for registration (this is NOT your character name):")
                username = await websocket.recv()
                # You can add more registration steps here if needed

                # Generate a random password
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

                # Insert the new user into the database
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)",
                               (email, username, password))
                connection.commit()
                cursor.close()
                connection.close()

                await websocket.send("Registration successful. Your username and password have been created.")
                return True
        except Error as e:
            print(f"Database error: {e}")
            return False
    else:
        return False

# Websocket server handler


async def server_handler(websocket, path):
    registration, db_config, ssl_config, server_config, messages = load_config()
    greeting_message = messages['greeting_with_registration'] if registration else messages['greeting_without_registration']
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
