# context_manager.py

from importlib import import_module

class ContextManager:
    def __init__(self, websocket, db_config, registration_enabled, messages):
        self.current_context = None
        self.websocket = websocket
        self.db_config = db_config
        self.registration_enabled = registration_enabled
        self.messages = messages

    async def set_context(self, context_name):
        try:
            print(f"Loading context: {context_name}")
            context_module = import_module(f'contexts.{context_name}')
            class_name = ''.join(word.capitalize() for word in context_name.split('_'))
            context_class = getattr(context_module, class_name)
            self.current_context = context_class(self.websocket, self.db_config, self.registration_enabled,
                                                 self.messages)
            print(f"Context set to: {context_name}")
            # Pass messages along with other configurations
            # Now properly await the send_greeting method
            if hasattr(self.current_context, 'send_greeting'):
                await self.current_context.send_greeting()

        except Exception as e:
            print(f"Error in set_context: {e}")

    async def handle_command(self, command):
        if self.current_context:
            await self.current_context.handle_command(command)
        else:
            print("No current context set.")
