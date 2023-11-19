import ssl
import asyncio
import websockets
from datetime import datetime

async def test_message():
    uri = "wss://localhost:7450"  # The address of the WebSocket server

    # Create a custom SSL context that trusts your self-signed certificate
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        # Send a test message
        test_msg = "Hello, Server!"
        await websocket.send(test_msg)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Sent: {test_msg}")

        # Receive and print the response from the server
        response = await websocket.recv()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Received: {response}")

# Run the client
asyncio.run(test_message())
