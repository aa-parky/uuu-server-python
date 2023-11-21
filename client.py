import asyncio
import websockets
import ssl
import datetime

async def websocket_client():
    uri = "wss://localhost:7450"  # Replace with your server's URI

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        greeting = await websocket.recv()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{current_time} Server says: {greeting}")

        while True:
            message_to_send = input("> ")
            await websocket.send(message_to_send)

            response = await websocket.recv()
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{current_time} > {response}")

            if response in ["Login successful.", "Login failed."]:
                break  # Exit loop after login attempt

# Run the client
asyncio.run(websocket_client())
