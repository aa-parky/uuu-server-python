import asyncio
import websockets
import ssl
import configparser
from register_user import register_user
from login import check_credentials
from lobby import display_motd


# Function to load configuration
def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    registration = config.getboolean('Settings', 'Registration')
    motd_enabled = config.getboolean('Settings', 'MOTD')
    db_config = config['Database']
    ssl_config = config['SSL']
    server_config = config['Server']
    messages = config['Messages']
    return registration, motd_enabled, db_config, ssl_config, server_config, messages


# Websocket server handler
async def server_handler(websocket, path):
    registration, motd_enabled, db_config, ssl_config, server_config, messages = load_config()
    greeting_key = 'greeting_with_registration' if registration else 'greeting_without_registration'
    greeting_message = messages[greeting_key]
    await websocket.send(greeting_message)

    try:
        while True:
            message = await websocket.recv()
            if message.lower() == "login":
                login_success = await check_credentials(websocket, db_config)
                if login_success:
                    await websocket.send("Login successful.")
                    print("Displaying MOTD...")
                    await display_motd(websocket)  # Directly call the display_motd function after a successful login
                else:
                    await websocket.send("Login failed.")  # This handles the login failure case
            elif message.lower() == "register" and registration:
                await register_user(websocket, db_config)
            else:
                await websocket.send("Unknown command. Try 'login' or 'register'.")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed.")


# Start the websocket server
async def start_server():
    _, _, _, ssl_config, server_config, _ = load_config()
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(ssl_config['certfile'], ssl_config['keyfile'])
    async with websockets.serve(server_handler, server_config['host'], int(server_config['port']), ssl=ssl_context):
        await asyncio.Future()


# Run the server
asyncio.run(start_server())
