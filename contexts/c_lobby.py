import asyncio
import configparser
import textwrap


class CLobby:
    def __init__(self, websocket, db_config, registration_enabled, messages, switch_context):
        self.websocket = websocket
        self.db_config = db_config
        self.registration_enabled = registration_enabled
        self.messages = messages
        self.switch_context = switch_context

        # Define available commands for this context
        self.available_commands = {
            'refresh': 'refresh screen',
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
        await self.display_motd()

    async def display_motd(self):
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
        config = configparser.ConfigParser()
        config.read('config.ini')
        motd_file = config['Messages']['motd_file']
        try:
            with open(motd_file, 'r') as file:
                motd_text = file.read()

                # Splitting the text into paragraphs and wrapping each paragraph
                paragraphs = motd_text.split('\n\n')
                wrapped_paragraphs = [textwrap.fill(paragraph, width=80) for paragraph in paragraphs]

                # Joining the paragraphs back together with two newlines as separator
                motd_text = '\n\n'.join(wrapped_paragraphs)

                return motd_text
        except FileNotFoundError:
            return "MOTD file not found."
    async def handle_command(self, command):
        if command.lower() == 'help':
            # Switch to the help context
            await self.switch_context('c_help')
        elif command.lower() == 'refresh':
           await  self.switch_context('c_lobby')
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
                "Unrecognized Lobby command. Type 'help', 'commands', 'manage', or 'messages' for more information.")

    async def display_available_commands(self):
        commands_info = "Available Commands:\n"
        for cmd, description in self.available_commands.items():
            commands_info += f"- {cmd}: {description}\n"
        await self.websocket.send(commands_info)
