import asyncio
import websockets
import ssl

async def websocket_client():
    uri = "wss://localhost:7450"  # Replace with your server's URI

    # Create an SSL context that does not verify the certificate
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        # Receive greeting message from the server
        greeting = await websocket.recv()
        print(f"Server says: {greeting}")

        # Client can reply or send messages to the server
        message_to_send = input("Enter your message: ")
        await websocket.send(message_to_send)
        print("Message sent to the server.")

        # Additional communication logic can be added here

# Run the client
asyncio.run(websocket_client())
