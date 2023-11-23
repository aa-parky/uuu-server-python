# contexts/c_server_auth.py

from login import check_credentials
from register_user import register_user


class CServerAuth:
    def __init__(self, websocket, db_config, registration_enabled, messages):
        self.websocket = websocket
        self.db_config = db_config
        self.registration_enabled = registration_enabled
        self.messages = messages

    async def send_greeting(self):
        greeting_key = 'greeting_with_registration' if self.registration_enabled else 'greeting_without_registration'
        greeting_message = self.messages[greeting_key]
        await self.websocket.send(greeting_message)

    async def handle_command(self, command):
        try:
            # Handle blank command
            if not command.strip():
                await self.websocket.send("No command entered. Type 'help' for available commands.")
                return

            if command.lower() == 'login':
                login_success = await check_credentials(self.websocket, self.db_config)
                if login_success:
                    await self.websocket.send("Login successful.")
                    # Transition logic can be added here
                else:
                    await self.websocket.send("Login failed.")

            elif command.lower() == 'register' and self.registration_enabled:
                await register_user(self.websocket, self.db_config)

            elif command.lower() == 'help':
                help_message = "You can type 'login' to login or 'register' to create a new account."
                await self.websocket.send(help_message)

            else:
                # Handle unrecognized command
                await self.websocket.send("Unrecognized command. Type 'help' for available commands.")

        except Exception as e:
            print(f"Error in CServerAuth handle_command: {e}")
