import asyncio
import websockets
import ssl
import datetime
import configparser
import threading
import queue

def load_config():
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
    config = configparser.ConfigParser()
    config.read('client_config.ini')
    return config.getboolean('Settings', 'display_current_time')


async def receive_messages(websocket):
    while True:
        response = await websocket.recv()
        display_time = read_display_current_time_setting()

        message_to_display = " ~ " + response
        if display_time:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message_to_display = f"{current_time} ~ {response}"

        print("\r" + message_to_display, end="\n> ", flush=True)  # Overwrite the current line and print the message


async def send_messages(websocket, message_queue):
    while True:
        message_to_send = await asyncio.to_thread(message_queue.get)
        await websocket.send(message_to_send)


def input_thread(message_queue):
    while True:
        message_to_send = input("> ")
        message_queue.put(message_to_send)


async def websocket_client():
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
