"""
This module provides a WebSocket-based client for a chat application.
It supports secure communication with SSL, handles user input in a separate thread,
and displays incoming messages asynchronously. Users can send messages and
optionally display the current time with each received message.
Configuration settings are loaded from a client_config.ini file.

Functions:
    load_config: Loads and returns client configuration settings from a .ini file.
    read_display_current_time_setting: Reads and returns the setting for
    displaying the current time with messages.
    receive_messages: Asynchronously receives and displays messages from the server.
    send_messages: Asynchronously sends messages to the server from a message queue.
    input_thread: Runs in a separate thread to handle user input without blocking.
    websocket_client: Initializes and runs the WebSocket client.
"""

import asyncio
import ssl
import datetime
import configparser
import threading
import queue
import websockets


def load_config():
    """
    Loads client configuration settings from 'client_config.ini' file.

    Returns:
        dict: A dictionary containing settings like display_current_time, uri, and port.
    """
    config = configparser.ConfigParser()
    config.read('client_config.ini')
    settings = config['Settings']
    server = config['Server']
    return {
        "display_current_time": settings.getboolean('display_current_time'),
        "uri": server['uri'],
        "port": server['port']
    }


def read_display_current_time_setting():
    """
    Reads the setting from 'client_config.ini' to determine if the current
    time should be displayed with messages.

    Returns:
        bool: True if the current time should be displayed, False otherwise.
    """
    config = configparser.ConfigParser()
    config.read('client_config.ini')
    return config.getboolean('Settings', 'display_current_time')


async def receive_messages(websocket):
    """
    Asynchronously receives messages from the server and displays them.

    Args:
        websocket (websockets.WebSocketClientProtocol): The WebSocket connection with the server.

    This function also checks the setting for displaying the current time
    and prepends it to the messages if required.
    """
    while True:
        response = await websocket.recv()
        display_time = read_display_current_time_setting()

        message_to_display = " ~ " + response
        if display_time:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message_to_display = f"{current_time} ~ {response}"

        print("\r" + message_to_display, end="\n> ", flush=True)


async def send_messages(websocket, message_queue):
    """
    Asynchronously sends messages to the server.

    Args:
        websocket (websockets.WebSocketClientProtocol): The WebSocket connection with the server.
        message_queue (queue.Queue): The queue of messages to be sent.

    This function continuously fetches messages from the message queue and sends them to the server.
    """
    while True:
        message_to_send = await asyncio.to_thread(message_queue.get)
        await websocket.send(message_to_send)


def input_thread(message_queue):
    """
    Runs in a separate thread to handle user input.

    Args:
        message_queue (queue.Queue): The queue to which user input messages are added.

    This function allows for user input without blocking the main thread.
    """
    while True:
        message_to_send = input("> ")
        message_queue.put(message_to_send)


async def websocket_client():
    """
    Initializes and runs the WebSocket client.

    This function sets up the SSL context, connects to the WebSocket server,
    and starts asynchronous tasks for receiving and sending messages.
    It also initializes a separate thread for handling user input.
    """
    config = load_config()
    uri = f"{config['uri']}:{config['port']}"

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    message_queue = queue.Queue()

    # Start the input thread
    threading.Thread(target=input_thread, args=(message_queue,), daemon=True).start()

    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        # Handle the initial greeting message
        greeting = await websocket.recv()
        display_time = read_display_current_time_setting()

        if display_time:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{current_time} ~ {greeting}")
        else:
            print(greeting + " ~")

        print("> ", end="", flush=True)  # Print the initial prompt

        # Start asynchronous tasks
        receive_task = asyncio.create_task(receive_messages(websocket))
        send_task = asyncio.create_task(send_messages(websocket, message_queue))

        # Wait for tasks to complete
        await asyncio.gather(receive_task, send_task)

# Run the client
asyncio.run(websocket_client())
