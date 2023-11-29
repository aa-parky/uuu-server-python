"""
This module contains the CManagement class for handling account management
activities in a multi-user dungeon (MUD) game. It offers functionalities for
password reset, navigating between different game contexts, and managing
account-related commands.

The CManagement class provides a user interface for account management tasks,
enabling players to perform actions like resetting their passwords, and accessing
help, messages, or returning to the lobby.
"""

import asyncio
import bcrypt
from mysql.connector import Error
from database import create_db_connection


class CManagement:
    """
        Represents the account management context within the MUD game.

        This class provides functionalities for managing player accounts, including
        password resets and displaying available commands. It handles user commands
        within the management context and directs players to appropriate actions or
        information.

        Attributes:
            websocket (WebSocket): The WebSocket connection for user interaction.
            db_config (dict): Configuration details for the database connection.
            registration_enabled (bool): Flag indicating if user registration is allowed.
            messages (list): List of messages for the user.
            switch_context (function): Function to switch to different game contexts.
            username (str): The username of the current user.
            available_commands (dict): Mapping of command names to their descriptions.

        Methods:
            initial_management_setup: Sets up the initial account management menu.
            handle_command: Processes user input commands within the management context.
            reset_password: Handles the process of resetting the user's password.
            verify_password: Verifies the user's current password.
            update_password_in_database: Updates the user's password in the database.
            display_available_commands: Shows a list of available commands to the user.
        """
    def __init__(self, config):
        self.websocket = config.websocket
        self.db_config = config.db_config
        self.registration_enabled = config.registration_enabled
        self.messages = config.messages
        self.switch_context = config.switch_context
        self.username = config.username

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
        """
            Sets up the initial display for the account management menu.

            This method sends an introductory message to the user upon entering the account
            management context, providing a starting point for account-related interactions.
            """
        await self.websocket.send("Account Management")

    async def handle_command(self, command):
        """
            Handles commands input by the user within the account management context.

            This method determines the appropriate action based on the user's command,
            such as resetting the password, switching contexts, or displaying available
            commands. Unrecognized commands are also addressed by providing user feedback.

            Args:
                command (str): The command entered by the user.
            """
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
            await self.websocket.send("Unrecognized Lobby command. Type 'help', 'commands', "
                                      "'manage', or ""'messages' for more information.")

    async def reset_password(self):
        """
           Manages the process of resetting the user's password.

           This method interacts with the user to change their password, including
           verifying the current password and confirming the new password before
           updating it in the database.

           Returns:
               None: This method does not return anything but communicates with the user
                     via the websocket.
           """
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
        """
            Verifies the user's current password against the stored password hash in the database.

            This method connects to the database and retrieves the stored password hash for
            the user. It then uses bcrypt to check if the provided password matches the
            stored hash.

            Args:
                password (str): The current password entered by the user for verification.

            Returns:
                bool: True if the provided password matches the stored hash, False otherwise
                      or in case of a database error.
            """
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
        """
           Updates the user's password in the database.

           This method hashes the new password using bcrypt and updates the user's
           password record in the database. It handles database connection, executes
           the update query, and commits the changes.

           Args:
               new_password (str): The new password to be set for the user.

           Returns:
               bool: True if the password update is successful, False otherwise, including
                     if a database error occurs.
           """
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

        connection = create_db_connection(self.db_config)
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE users SET password = %s WHERE username = %s",
                               (hashed_password, self.username))
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
        """
            Displays a list of available commands to the user within the management context.

            This method sends a formatted list of commands that the user can execute in
            the management context, along with a brief description of each command.

            Returns:
                None: This method does not return anything but communicates with the user
                      via the websocket.
            """
        commands_info = "Available Commands:\n"
        for cmd, description in self.available_commands.items():
            commands_info += f"- {cmd}: {description}\n"
        await self.websocket.send(commands_info)
