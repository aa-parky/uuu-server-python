import asyncio
import websockets
import ssl

async def echo(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")
        await websocket.send(f"Echo: {message}")

async def main():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile="C:/MAMP/bin/certs/uuu-websocket-test.cert",
                                keyfile="C:/MAMP/bin/certs/uuu-websocket-test.key")

    # Change the port to 7449 to match your URL
    async with websockets.serve(echo, "localhost", 7450, ssl=ssl_context):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
