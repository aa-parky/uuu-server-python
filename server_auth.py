import asyncio
import websockets
import ssl
import configparser
from context_manager import ContextManager
from login import handle_authentication  # Updated import
from connections import connected_users  # Import the connected_users dictionary


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


async def server_handler(websocket, path):
    registration, motd_enabled, db_config, ssl_config, server_config, messages = load_config()

    while True:
        player_context_manager = ContextManager(websocket, db_config, registration, messages)

        auth_status, action, username = await handle_authentication(websocket, db_config, registration)

        if auth_status:
            player_context_manager.username = username
            await player_context_manager.set_context('c_lobby')
            try:
                while True:
                    message = await websocket.recv()
                    await player_context_manager.handle_command(message)
            except websockets.exceptions.ConnectionClosed:
                print(f"Connection closed for {username}.")
                if username in connected_users:
                    del connected_users[username]  # Remove user from connected users
                break
        else:
            await handle_authentication(websocket, db_config, registration)


# Start the websocket server
async def start_server():
    _, _, _, ssl_config, server_config, _ = load_config()
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(ssl_config['certfile'], ssl_config['keyfile'])
    async with websockets.serve(server_handler, server_config['host'], int(server_config['port']), ssl=ssl_context):
        await asyncio.Future()

# Run the server
asyncio.run(start_server())
