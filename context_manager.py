from importlib import import_module

class ContextManager:
    def __init__(self, websocket, db_config, registration_enabled, messages):
        # Initialize the ContextManager with necessary attributes
        self.current_context = None  # To keep track of the current context
        self.websocket = websocket  # Websocket for communication
        self.db_config = db_config  # Database configuration
        self.registration_enabled = registration_enabled  # Flag for registration status
        self.messages = messages  # Messages used in different contexts
        self.username = None  # Add this line to store the username

    async def switch_context(self, new_context_name, additional_args=None):
        # Method to switch the context
        await self.set_context(new_context_name, additional_args=additional_args)

    async def set_context(self, context_name, additional_args=None):
        # Method to set a new context based on the context name
        try:
            # Include the player's username in the log message if available
            username_info = f" for player: {self.username}" if self.username else ""
            print(f"Loading context: {context_name}{username_info}")
            # Dynamically import the module corresponding to the context
            context_module = import_module(f'contexts.{context_name}')
            # Generate the class name from the context name
            class_name = ''.join(word.capitalize() for word in context_name.split('_'))
            # Retrieve the class from the imported module
            context_class = getattr(context_module, class_name)

            # Initialize the context with additional arguments if provided
            if additional_args is not None:
                self.current_context = context_class(self.websocket, self.db_config, self.registration_enabled,
                                                     self.messages, self.switch_context, **additional_args)
            else:
                self.current_context = context_class(self.websocket, self.db_config, self.registration_enabled,
                                                     self.messages, self.switch_context)

            print(f"Context set to: {context_name}{username_info}")
            # ... rest of the existing code for set_context
            # If the current context has a send_greeting method, call it
            if hasattr(self.current_context, 'send_greeting'):
                await self.current_context.send_greeting()

        except Exception as e:
            # Handle any exceptions during context setting
            print(f"Error in set_context: {e}")

    async def handle_command(self, command):
        # Method to handle commands in the current context
        if self.current_context:
            # Delegate the command handling to the current context
            await self.current_context.handle_command(command)
        else:
            # Handle the case where no context is set
            print("No current context set.")
