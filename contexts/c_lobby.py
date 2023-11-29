"""
This module contains the CLobby class, which represents the lobby context in a
multi-user dungeon (MUD) game. It provides functionalities for displaying the
Message of the Day (MOTD), listing connected users, and handling various lobby-specific
commands.

The CLobby class offers a user interface for players once they log in, allowing
them to interact with different parts of the game, receive game messages, and navigate
to other contexts such as help, management, or messages. It also includes methods
to display a list of available commands in the lobby and handle command execution.
"""

import asyncio
import configparser
import textwrap
from connections import connected_users


class CLobby:
    """
    CLobby: Represents the lobby context for the MUD game, handling initial user
            interaction after login, and navigating to other contexts.

        Attributes:
            websocket (WebSocket): The WebSocket connection for this lobby.
            db_config (dict): The configuration for the database.
            registration_enabled (bool): Whether user registration is enabled.
            messages (dict): A dictionary for storing messages.
            switch_context (function): A function to switch the user's context.
            username (str): The username of the current user.
            available_commands (dict): A dictionary of available commands and
            their descriptions.
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
            'refresh': 'refresh screen',
            'who': 'list connected users',
            'help': 'Get help about commands',
            'commands': 'List all available commands',
            'manage': 'Enter management context',
            'messages': 'Enter messages context',
            '/quit': 'type /quit to close exit the world'
            # ... other commands ...
        }

        # Run the initial lobby setup, like displaying MOTD
        asyncio.create_task(self.initial_lobby_setup())

    async def initial_lobby_setup(self):
        """
         Method: initial_lobby_setup(): Performs the initial setup of the lobby,
            including displaying MOTD.
        """
        await self.display_motd()

    async def display_motd(self):
        """
        Method: display_motd(): Displays the Message of the Day if enabled.
        """
        config = configparser.ConfigParser()
        config.read('config.ini')
        motd_enabled = config.getboolean('Settings', 'MOTD')

        if motd_enabled:
            motd = self.load_motd()
            await self.websocket.send(motd)
        else:
            await self.websocket.send("Welcome to the Lobby")

    @staticmethod
    def load_motd():
        """
        Method: load_motd(): Loads the MOTD from a file and formats it for display.
        """
        config = configparser.ConfigParser()
        config.read('config.ini')
        motd_file = config['Messages']['motd_file']
        try:
            with open(motd_file, 'r', encoding='utf-8') as file:
                motd_text = file.read()

                # Splitting the text into paragraphs and wrapping each paragraph
                paragraphs = motd_text.split('\n\n')
                wrapped_paragraphs = [textwrap.fill(paragraph, width=80)
                                      for paragraph in paragraphs]

                # Joining the paragraphs back together with two newlines as separator
                motd_text = '\n\n'.join(wrapped_paragraphs)

                return motd_text
        except FileNotFoundError:
            return "MOTD file not found."

    async def handle_command(self, command):
        """
        Method: handle_command(command): Handles user commands.
        """
        if command.lower() == 'help':
            # Switch to the help context
            await self.switch_context('c_help')
        elif command.lower() == 'who':
            await self.list_connected_users()
        elif command.lower() == 'refresh':
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
                "Unrecognized Lobby command. Type 'help', 'commands', 'manage', "
                "or 'messages' for more information.")

    async def list_connected_users(self):
        """
        method: list the connected users
        """
        user_list = "Connected users:\n" + "\n".join(connected_users.keys())
        await self.websocket.send(user_list)

    async def display_available_commands(self):
        """
        Method: list available commands
        """
        commands_info = "Available Commands:\n"
        for cmd, description in self.available_commands.items():
            commands_info += f"- {cmd}: {description}\n"
        await self.websocket.send(commands_info)
