import asyncio
import shutil

from aidial_client import Dial
from httpx import stream

from task.clients.client import DialClient
from task.clients.custom_client import DialClientCustom
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role

class Terminal():
    _width: int = 0
    def __init__(self):
        try:
            size = shutil.get_terminal_size()
            self._width = size.columns
        except OSError:
            self._width = 80

    def print_full_width_message(self, message: str) -> None:
        message_len = len(message) + 2 # indent

        print('')
        if message_len >= self._width:
            print('*' * self._width)
            print(message)
            print('*' * self._width)
        else:
            left_width = (self._width - message_len) // 2
            right_width = self._width - message_len - left_width
            print('*' * left_width, message, '*' * right_width)
        print('')
    def print(self, message: str) -> None:
        print(message)

async def start(stream: bool) -> None:
    #TODO:
    # 1.1. Create DialClient
    # (you can get available deployment_name via https://ai-proxy.lab.epam.com/openai/models
    #  you can import Postman collection to make a request, file in the project root `dial-basics.postman_collection.json`
    #  don't forget to add your API_KEY)
    # 1.2. Create CustomDialClient
    # 2. Create Conversation object
    # 3. Get System prompt from console or use default -> constants.DEFAULT_SYSTEM_PROMPT and add to conversation
    #    messages.
    # 4. Use infinite cycle (while True) and get yser message from console
    # 5. If user message is `exit` then stop the loop
    # 6. Add user message to conversation history (role 'user')
    # 7. If `stream` param is true -> call DialClient#stream_completion()
    #    else -> call DialClient#get_completion()
    # 8. Add generated message to history
    # 9. Test it with DialClient and CustomDialClient
    # 10. In CustomDialClient add print of whole request and response to see what you send and what you get in response
    # raise NotImplementedError
    dial = DialClientCustom(deployment_name='gpt-4o')
    term = Terminal()

    conversation = Conversation()
    conversation.add_message(Message(role=Role.SYSTEM, content=DEFAULT_SYSTEM_PROMPT))
    print('Type your message to console. Type "exit" to close the conversation')
    while True:
        print('')
        term.print_full_width_message('User Message')
        user_message = input(">").strip()

        if user_message == 'exit':
            term.print_full_width_message('User ended conversation')
            break

        conversation.add_message(Message(role=Role.USER, content=user_message))

        term.print_full_width_message('AI response')
        messages = conversation.get_messages()
        result = await dial.stream_completion(messages) if stream == True else dial.get_completion(messages)

        conversation.add_message(result)


asyncio.run(
    start(True)
)
