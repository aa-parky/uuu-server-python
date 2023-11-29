"""
This module contains the CMessages class, which handles the messages context in a
multi-user dungeon (MUD) game. It provides functionalities for managing in-game
messages, navigating between different contexts, and handling user commands related
to messages.

The CMessages class allows players to interact with message-related features of the
game, such as viewing messages, returning to the lobby, and accessing the help menu.
It includes methods to display the message menu, handle user commands within the
messages context, and display a list of available commands.
"""

import asyncio


class CMessages:
    """
        A class representing the messages context within the MUD game.

        This class is responsible for handling the interactions and commands that are
        specific to the messages context, including navigating back to the lobby, managing
        messages, and accessing help and other contexts.

        Attributes:
            websocket (WebSocket): The WebSocket connection for user interaction.
            db_config (dict): Configuration details for the database connection.
            registration_enabled (bool): Flag indicating if new user registration is allowed.
            messages (list): List of messages for the user.
            switch_context (function): Function to switch to different game contexts.
            username (str): The username of the current user.
            available_commands (dict): A dictionary mapping command names to their descriptions.

        Methods:
            initial_messages_setup: Sets up the initial message menu display.
            handle_command: Handles commands input by the user in the messages' context.
            display_available_commands: Displays a list of available commands to the user.
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
            'help': 'Display the help menu',
            '/quit': 'type /quit to close exit the world'
            # ... other commands ...
        }

        # Run the initial lobby setup, like displaying MOTD
        asyncio.create_task(self.initial_messages_setup())

    async def initial_messages_setup(self):
        """
            Sets up the initial message menu display when the user enters the messages' context.

            This method is an asynchronous task that sends a greeting or introductory message
            to the user upon entering the messages context, setting the stage for further
            message-related interactions.
            """
        await self.websocket.send("Message Menu")

    async def handle_command(self, command):
        """
           Handles the commands input by the user within the messages' context.

           Based on the user's input command, this method determines the appropriate action,
           which may include switching to another context (such as lobby or management),
           displaying help, or showing the list of available commands. Unrecognized commands
           are also handled by providing feedback to the user.

           Args:
               command (str): The command input by the user.
           """
        if command.lower() == 'lobby':
            # Switch to the help context
            await self.switch_context('c_lobby')
        elif command.lower() == 'manage':
            # Switch to the management context
            await self.switch_context('c_management')
        elif command.lower() == 'help':
            # Switch to the messages context
            await self.switch_context('c_help')
        elif command.lower() == 'commands':
            await self.display_available_commands()
        else:
            # Handle unrecognized command or general lobby actions
            await self.websocket.send(
                "Unrecognized Messages Command. Type 'lobby', 'commands', 'manage',"
                " or 'help' for more information.")

    async def display_available_commands(self):
        """
           Displays a list of available commands to the user in the messages' context.

           This method asynchronously sends a list of commands that the user can execute in
           the messages context, along with a brief description of each command, helping
           users understand their options for interaction.
           """
        commands_info = "Available Commands:\n"
        for cmd, description in self.available_commands.items():
            commands_info += f"- {cmd}: {description}\n"
        await self.websocket.send(commands_info)
