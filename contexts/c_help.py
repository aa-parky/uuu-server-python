import asyncio
import configparser
import textwrap


class CHelp:
    def __init__(self, websocket, _db_config, _registration_enabled, _messages, switch_context, *_):
        self.websocket = websocket
        self.switch_context = switch_context

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
        asyncio.create_task(self.initial_lobby_setup())

    async def initial_lobby_setup(self):
        await self.websocket.send("Help Menu")

    async def handle_command(self, command):
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
                "Unrecognized Lobby command. Type 'lobby', 'commands', 'manage', or 'messages' for more information.")

    async def display_available_commands(self):
        commands_info = "Available Commands:\n"
        for cmd, description in self.available_commands.items():
            commands_info += f"- {cmd}: {description}\n"
        await self.websocket.send(commands_info)
