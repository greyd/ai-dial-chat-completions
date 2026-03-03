from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT, API_KEY
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)

        if API_KEY == "":
            raise ValueError("API_KEY cannot be empty")

        self.dial_client = Dial(api_key=API_KEY, base_url=DIAL_ENDPOINT)
        self.dial_client_async = AsyncDial(api_key=API_KEY, base_url=DIAL_ENDPOINT)
        #TODO:
        # Documentation: https://pypi.org/project/aidial-client/ (here you can find how to create and use these clients)
        # 1. Create Dial client
        # 2. Create AsyncDial client

    def get_completion(self, messages: list[Message]) -> Message:
        #TODO:
        # 1. Create chat completions with client
        #    Hint: to unpack messages you can use the `to_dict()` method from Message object
        # 2. Get content from response, print it and return message with assistant role and content
        # 3. If choices are not present then raise Exception("No choices in response found")
        # raise NotImplementedError
        completion = self.dial_client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=False,
            messages=[message.to_dict() for message in messages],
        )
        if completion.choices is None or len(completion.choices) == 0:
            raise Exception('No choices in response found')
        responce = completion.choices[0].message.content
        print(responce)
        return Message(Role.AI, responce)

    async def stream_completion(self, messages: list[Message]) -> Message:
        #TODO:
        # 1. Create chat completions with async client
        #    Hint: don't forget to add `stream=True` in call.
        # 2. Create array with `contents` name (here we will collect all content chunks)
        # 3. Make async loop from `chunks` (from 1st step)
        # 4. Print content chunk and collect it contents array
        # 5. Print empty row `print()` (it will represent the end of streaming and in console we will print input from a new line)
        # 6. Return Message with assistant role and message collected content
        contents = []
        completion = await self.dial_client_async.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=True,
            messages=[message.to_dict() for message in messages],
        )

        async for chunk in completion:
            if chunk.choices is None or len(chunk.choices) == 0:
                raise Exception('No choices in response found')
            value = chunk.choices[0].delta.content
            if value is None:
                break
            print(value, end='')
            contents.append(value)

        return Message(Role.AI, ''.join(contents))
