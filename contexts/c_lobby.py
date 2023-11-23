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
                motd_text = '\n' + file.read()
                motd_text = textwrap.fill(motd_text, width=80)
                return motd_text
        except FileNotFoundError:
            return "MOTD file not found."

    async def handle_command(self, command):
        if command.lower() == 'help':
            # Switch to the help context
            await self.switch_context('c_help')
        elif command.lower() == 'manage':
            # Switch to the management context
            await self.switch_context('c_management')
        # ... handle other lobby-specific commands here ...
        else:
            # Handle unrecognized command or general lobby actions
            await self.websocket.send("Unrecognized command in lobby. Type 'help' for assistance.")
