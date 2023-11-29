"""
This module provides the functionality to manage and switch between different
contexts (like lobby, messages, management) in a multi-user dungeon (MUD) game.
It includes the classes necessary for maintaining and managing these contexts,
as well as handling user commands within them.

Classes:
    Config: A helper class for passing configuration information to contexts.
    ContextManager: Manages the current active context in the game and handles
                    the switching and command processing within these contexts.
"""

from importlib import import_module

class Config:
    """
       Helper class to store and pass configuration information to different game contexts.

       This class is used to create a configuration object that can be passed to
       different context classes in the game. It stores various configuration parameters
       and user-specific information.

       Attributes:
           websocket (WebSocket): The WebSocket connection for user interaction.
           db_config (dict): Configuration details for the database connection.
           registration_enabled (bool): Indicates if new user registrations are allowed.
           messages (list): A list of messages relevant to the user.
           switch_context (function): A reference to the function used to switch contexts.
           username (str, optional): The username of the player. Defaults to None.
       """
    def __init__(self, websocket, db_config, registration_enabled,
                 messages, switch_context, username=None):
        self.websocket = websocket
        self.db_config = db_config
        self.registration_enabled = registration_enabled
        self.messages = messages
        self.switch_context = switch_context
        self.username = username
class ContextManager:
    """
        Manages the current active context in the MUD game and handles switching between them.

        This class is responsible for initializing and switching between different
        contexts based on user commands or game events. It also relays commands to the
        currently active context for processing.

        Attributes:
            current_context (object): The current active context object.
            websocket (WebSocket): The WebSocket connection for user interaction.
            db_config (dict): Configuration details for the database connection.
            registration_enabled (bool): Indicates if new user registrations are allowed.
            messages (list): A list of messages relevant to the user.
            username (str, optional): The username of the player. Defaults to None.

        Methods:
            switch_context: Switches to a new context based on the given context name.
            set_context: Initializes and sets the specified context as the current context.
            handle_command: Passes commands to the current context for processing.
        """
    def __init__(self, websocket, db_config, registration_enabled, messages, username=None):
        self.current_context = None
        self.websocket = websocket
        self.db_config = db_config
        self.registration_enabled = registration_enabled
        self.messages = messages
        self.username = username  # Storing the username

    async def switch_context(self, new_context_name, additional_args=None):
        """
           Switches to the specified context.

           Asynchronously sets a new context as the current active context, potentially
           with additional arguments.

           Args:
               new_context_name (str): The name of the new context to switch to.
               additional_args (dict, optional): Additional arguments to pass to the new context.
                                                 Defaults to None.
           """
        await self.set_context(new_context_name, additional_args=additional_args)

    async def set_context(self, context_name, additional_args=None):
        """
            Initializes and sets the specified context as the current context.

            Dynamically loads the context class based on the context name, creates an
            instance of it, and sets it as the current context. It also handles errors
            during context initialization.

            Args:
                context_name (str): The name of the context to initialize and set.
                additional_args (dict, optional): Additional arguments to pass to the context class.
                                                  Defaults to None.
            """
        try:
            username_info = f" for player: {self.username}" if self.username else ""
            print(f"Loading context: {context_name}{username_info}")

            context_module = import_module(f'contexts.{context_name}')
            class_name = ''.join(word.capitalize() for word in context_name.split('_'))
            context_class = getattr(context_module, class_name)

            # Create a config object with all the required parameters
            config = Config(
                websocket=self.websocket,
                db_config=self.db_config,
                registration_enabled=self.registration_enabled,
                messages=self.messages,
                switch_context=self.switch_context,
                username=self.username,
            )

            # Initialize the context with the config object
            if additional_args is not None:
                self.current_context = context_class(config, **additional_args)
            else:
                self.current_context = context_class(config)

            print(f"Context set to: {context_name}{username_info}")

            if hasattr(self.current_context, 'send_greeting'):
                await self.current_context.send_greeting()

        except Exception as e:
            print(f"Error in set_context: {e}")

    async def handle_command(self, command):
        """
           Passes the given command to the current context for processing.

           If a current context is set, this method passes the user input command to
           that context's handle_command method. If no context is set, it outputs an
           error message.

           Args:
               command (str): The command input by the user to be handled.
           """
        if self.current_context:
            await self.current_context.handle_command(command)
        else:
            print("No current context set.")
