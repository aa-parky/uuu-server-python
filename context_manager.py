from importlib import import_module

class ContextManager:
    def __init__(self, websocket, db_config, registration_enabled, messages, username=None):
        self.current_context = None
        self.websocket = websocket
        self.db_config = db_config
        self.registration_enabled = registration_enabled
        self.messages = messages
        self.username = username  # Storing the username

    async def switch_context(self, new_context_name, additional_args=None):
        await self.set_context(new_context_name, additional_args=additional_args)

    async def set_context(self, context_name, additional_args=None):
        try:
            username_info = f" for player: {self.username}" if self.username else ""
            print(f"Loading context: {context_name}{username_info}")

            context_module = import_module(f'contexts.{context_name}')
            class_name = ''.join(word.capitalize() for word in context_name.split('_'))
            context_class = getattr(context_module, class_name)

            # Initialize the context with the username and additional arguments if provided
            if additional_args is not None:
                self.current_context = context_class(self.websocket, self.db_config, self.registration_enabled,
                                                     self.messages, self.switch_context, self.username, **additional_args)
            else:
                self.current_context = context_class(self.websocket, self.db_config, self.registration_enabled,
                                                     self.messages, self.switch_context, self.username)

            print(f"Context set to: {context_name}{username_info}")

            if hasattr(self.current_context, 'send_greeting'):
                await self.current_context.send_greeting()

        except Exception as e:
            print(f"Error in set_context: {e}")

    async def handle_command(self, command):
        if self.current_context:
            await self.current_context.handle_command(command)
        else:
            print("No current context set.")
