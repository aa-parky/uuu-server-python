import asyncio
import bcrypt
from database import create_db_connection
from mysql.connector import Error


class CManagement:
    def __init__(self, websocket, db_config, registration_enabled, messages, switch_context, username):
        self.websocket = websocket
        self.db_config = db_config
        self.registration_enabled = registration_enabled
        self.messages = messages
        self.switch_context = switch_context
        self.username = username  # Storing the username

        # Define available commands for this context
        self.available_commands = {
            'lobby': 'Return to the lobby',
            'reset': 'Reset your password',  # Use lowercase for consistency
            'commands': 'List all available commands',
            'messages': 'Enter your message screen',
            '/quit': 'type /quit to close exit the world'
            # ... other commands ...
        }

        asyncio.create_task(self.initial_management_setup())

    async def initial_management_setup(self):
        await self.websocket.send("Account Management")

    async def handle_command(self, command):
        if command.lower() == 'help':
            await self.switch_context('c_help')
        elif command.lower() == 'reset':
            await self.reset_password()
        elif command.lower() == 'lobby':
            await self.switch_context('c_lobby')
        elif command.lower() == 'messages':
            await self.switch_context('c_messages')
        elif command.lower() == 'commands':
            await self.display_available_commands()
        else:
            await self.websocket.send("Unrecognized Lobby command. Type 'help', 'commands', 'manage', or "
                                      "'messages' for more information.")

    async def reset_password(self):
        await self.websocket.send("Enter your current password:")
        current_password = await self.websocket.recv()

        # Verify current password
        if not await self.verify_password(current_password):
            await self.websocket.send("Incorrect current password.")
            return

        # New password input and validation
        await self.websocket.send("Enter your new password:")
        new_password = await self.websocket.recv()
        await self.websocket.send("Confirm your new password:")
        confirm_password = await self.websocket.recv()

        if new_password != confirm_password:
            await self.websocket.send("Passwords do not match.")
            return

        # Update password in the database
        if await self.update_password_in_database(new_password):
            await self.websocket.send("Password successfully changed.")
        else:
            await self.websocket.send("Failed to change the password.")

    async def verify_password(self, password):
        connection = create_db_connection(self.db_config)
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT password FROM users WHERE username = %s", (self.username,))
                user_password_hash = cursor.fetchone()
                cursor.close()
                return bcrypt.checkpw(password.encode(), user_password_hash[0].encode())
            except Error as e:
                print(f"Database error: {e}")
                return False
            finally:
                connection.close()
        else:
            return False

    async def update_password_in_database(self, new_password):
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

        connection = create_db_connection(self.db_config)
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_password, self.username))
                connection.commit()
                cursor.close()
                return True
            except Error as e:
                print(f"Database error: {e}")
                return False
            finally:
                connection.close()
        else:
            return False

    async def display_available_commands(self):
        commands_info = "Available Commands:\n"
        for cmd, description in self.available_commands.items():
            commands_info += f"- {cmd}: {description}\n"
        await self.websocket.send(commands_info)
