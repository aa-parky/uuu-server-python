import asyncio
import websockets
import ssl
import datetime
import aioconsole
import configparser


# Function to read the display_current_time setting from client_config.ini
def read_display_current_time_setting():
    config = configparser.ConfigParser()
    config.read('client_config.ini')
    return config.getboolean('Settings', 'display_current_time')


async def receive_messages(websocket):
    while True:
        response = await websocket.recv()
        display_time = read_display_current_time_setting()

        if display_time:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{current_time} > {response}")
        else:
            print(response)


async def send_messages(websocket):
    while True:
        message_to_send = await aioconsole.ainput("> ")
        await websocket.send(message_to_send)


async def websocket_client():
    uri = "wss://localhost:7450"  # Replace with your server's URI

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        greeting = await websocket.recv()
        display_time = read_display_current_time_setting()

        if display_time:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{current_time}: {greeting}")
        else:
            print(greeting)

        # Start asynchronous tasks
        receive_task = asyncio.create_task(receive_messages(websocket))
        send_task = asyncio.create_task(send_messages(websocket))

        # Wait for tasks to complete
        await asyncio.gather(receive_task, send_task)


# Run the client
asyncio.run(websocket_client())
