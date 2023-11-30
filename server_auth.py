"""
This module sets up and runs a WebSocket server for a multiplayer online game.
It handles user authentication, manages active connections, and facilitates communication
between the server and connected clients. The server uses SSL for secure communication
and supports functionalities like user registration and handling user commands
within the game context.

Functions:
    load_config: Loads and returns various configuration settings from a .ini file.
    server_handler: Manages the WebSocket connection for each client,
    handling authentication and communication.start_server: Initializes
    and starts the WebSocket server with SSL context.
"""

import asyncio
import ssl
import configparser
import websockets
from context_manager import ContextManager
from login import handle_authentication
from connections import connected_users  # Import the connected_users dictionary

def load_config():
    """
    Loads configuration settings from the 'config.ini' file.

    Reads server, database, SSL, and other settings from the configuration file and
    returns them for use in server initialization and client handling.

    Returns:
        tuple: Contains configurations for registration, database, SSL, server, and messages.
    """
    config = configparser.ConfigParser()
    config.read('config.ini')
    registration = config.getboolean('Settings', 'Registration')
    db_config = config['Database']
    ssl_config = config['SSL']
    server_config = config['Server']
    messages = config['Messages']
    return registration, db_config, ssl_config, server_config, messages

async def server_handler(websocket, _path):
    """
    Handles incoming WebSocket connections.

    Manages each client's connection lifecycle including authentication, context setting,
    and command handling. It also handles connection closure and removes the user from
    the list of connected users if the connection is lost.

    Args:
        websocket (websockets.WebSocketServerProtocol): The WebSocket connection with the client.
        _path (str): The URL path which the client is trying to connect to.
    """
    registration, db_config, _, _, messages = load_config()

    while True:
        player_context_manager = ContextManager(websocket, db_config, registration, messages)

        auth_status, _, username = await handle_authentication(websocket, db_config, registration)

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

async def start_server():
    """
    Initializes and starts the WebSocket server.

    Configures the SSL context for secure communications and starts the server
    on the specified host and port. It remains active to handle incoming connections
    until manually stopped.

    """
    _, _, ssl_config, server_config, _ = load_config()
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(ssl_config['certfile'], ssl_config['keyfile'])
    async with websockets.serve(server_handler, server_config['host'],
                                int(server_config['port']), ssl=ssl_context):
        await asyncio.Future()

# Run the server
asyncio.run(start_server())
