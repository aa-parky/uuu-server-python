"""
This module contains the CHelp class, which handles the help context in a
multi-user dungeon (MUD) game. It provides functionalities for assisting players
with available commands, navigating between different contexts, and managing
help-related user interactions.

The CHelp class offers an interface for players to access help and information
about game commands, as well as navigate to other game contexts like lobby,
messages, or account management.
"""

import asyncio


class CHelp:
    """
       A class representing the help context within the MUD game.

       This class is responsible for providing assistance and information to the
       player, including a list of available commands and navigation options within
       the game. It handles user input within the help context and directs the player
       to appropriate actions or information.

       Attributes:
           websocket (WebSocket): The WebSocket connection for user interaction.
           db_config (dict): Configuration details for the database connection.
           registration_enabled (bool): Flag indicating if new user registration is allowed.
           messages (list): List of messages for the user.
           switch_context (function): Function to switch to different game contexts.
           username (str): The username of the current user.
           available_commands (dict): A dictionary mapping command names to their descriptions.

       Methods:
           initial_help_setup: Initiates the help menu display.
           handle_command: Handles user input commands within the help context.
           display_available_commands: Shows the list of available commands to the user.
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
            'commands': 'List all available commands',
            'manage': 'Enter account management screen',
            'messages': 'Enter your message screen',
            '/quit': 'type /quit to close exit the world'
            # ... other commands ...
        }

        # Run the initial lobby setup, like displaying MOTD
        asyncio.create_task(self.initial_help_setup())

    async def initial_help_setup(self):
        """
           Initiates the help menu display for the user upon entering the help context.

           This method sends an introductory help menu message to the user, providing
           a starting point for accessing help and information within the game.
           """
        await self.websocket.send("Help Menu")

    async def handle_command(self, command):
        """
           Handles commands entered by the user within the help context.

           This method processes the user's input command and takes appropriate actions,
           such as switching to different game contexts or displaying available commands.
           It also handles unrecognized commands by informing the user.

           Args:
               command (str): The command entered by the user.
           """
        if command.lower() == 'lobby':
            # Switch to the help context
            await self.switch_context('c_lobby')
        elif command.lower() == 'manage':
            # Switch to the management context
            await self.switch_context('c_management')
        elif command.lower() == 'messages':
            # Switch to the messages context
            await self.switch_context('c_messages')
        elif command.lower() == 'commands':
            await self.display_available_commands()
        else:
            # Handle unrecognized command or general lobby actions
            await self.websocket.send(
                "Unrecognized Lobby command. Type 'lobby', 'commands', 'manage', "
                "or 'messages' for more information.")

    async def display_available_commands(self):
        """
           Displays a list of available commands to the user within the help context.

           This method asynchronously sends a formatted list of commands that the user
           can execute in the help context, each with a brief description, aiding the
           user in understanding the options available for interaction.
           """
        commands_info = "Available Commands:\n"
        for cmd, description in self.available_commands.items():
            commands_info += f"- {cmd}: {description}\n"
        await self.websocket.send(commands_info)
