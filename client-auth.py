import ssl
import asyncio
import websockets

async def interact_with_server():
    uri = "wss://localhost:7450"

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        # Receive the initial prompt from the server
        server_message = await websocket.recv()
        print(f"Server says: {server_message}")

        # Determine if registration is enabled
        registration_enabled = "Register" in server_message

        # User input for action
        action_prompt = "Enter your action (login): " if not registration_enabled else "Enter your action (login or register): "
        action = input(action_prompt).lower()

        if action == "login":
            username = input("Enter username: ")
            password = input("Enter password: ")
            await websocket.send(f"login {username} {password}")
        elif action == "register" and registration_enabled:
            email = input("Enter email: ")
            await websocket.send(f"register {email}")
        else:
            print("Invalid action.")

        # Wait for server response
        response = await websocket.recv()
        print(f"Server response: {response}")

# Run the client interaction
asyncio.run(interact_with_server())
