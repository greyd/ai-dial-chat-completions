import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT, API_KEY
from task.models.message import Message
from task.models.role import Role


class DialClientCustom(BaseClient):
    _endpoint: str
    _api_key: str
    _headers: dict

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"
        self._api_key = API_KEY
    def get_completion(self, messages: list[Message]) -> Message:
        #TODO:
        # Take a look at README.md of how the request and regular response are looks like!
        # 1. Create headers dict with api-key and Content-Type
        # 2. Create request_data dictionary with:
        #   - "messages": convert messages list to dict format using msg.to_dict() for each message
        # 3. Make POST request using requests.post() with:
        #   - URL: self._endpoint
        #   - headers: headers from step 1
        #   - json: request_data from step 2
        # 4. Get content from response, print it and return message with assistant role and content
        # 5. If status code != 200 then raise Exception with format: f"HTTP {response.status_code}: {response.text}"

        headers = {
            "Content-Type": "application/json",
            "api-key": self._api_key
        }
        request_data = {
            "messages": [message.to_dict() for message in messages]
        }

        response = requests.post(self._endpoint, json=request_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            choices = data.get('choices', [])
            if len(choices) == 0:
                raise ValueError('No choices has been returned')
            content = choices[0]['message']['content']
            return Message(role=Role.AI, content=content)
        else:
            raise Exception(f'HTTP call failed with status code {response.status_code}: {response.text}')

    async def stream_completion(self, messages: list[Message]) -> Message:
        #TODO:
        # Take a look at README.md of how the request and streamed response chunks are looks like!
        # 1. Create headers dict with api-key and Content-Type
        # 2. Create request_data dictionary with:
        #    - "stream": True  (enable streaming)
        #    - "messages": convert messages list to dict format using msg.to_dict() for each message
        # 3. Create empty list called 'contents' to store content snippets
        # 4. Create aiohttp.ClientSession() using 'async with' context manager
        # 5. Inside session, make POST request using session.post() with:
        #    - URL: self._endpoint
        #    - json: request_data from step 2
        #    - headers: headers from step 1
        #    - Use 'async with' context manager for response
        # 6. Get content from chunks (don't forget that chunk start with `data: `, final chunk is `data: [DONE]`), print
        #    chunks, collect them and return as assistant message
        headers = {
            "Content-Type": "application/json",
            "api-key": self._api_key
        }
        request_data = {
            "stream": True,
            "messages": [message.to_dict() for message in messages]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self._endpoint, json=request_data, headers=headers) as response:
                content = []
                acc = []

                async for chunk in response.content.iter_chunked(256):
                    current_chunk = chunk.decode('utf-8')
                    acc.append(current_chunk)
                    line = ''.join(acc)

                    while True:
                        next_idx = line.find('data:', 1)
                        if next_idx == -1:
                            acc = [line]
                            break
                        str_data = line[:next_idx].replace("'", '"').replace('data:', '')
                        try:
                            parsed_json = json.loads(str_data)
                            delta = parsed_json['choices'][0]['delta']
                            if 'content' in delta:
                                value = delta['content']
                                content.append(value)

                                if value is None:
                                    break
                                print(value, end='')
                            else:
                                pass
                        except json.decoder.JSONDecodeError:
                            pass
                        line = line[next_idx:]



                return Message(role=Role.AI, content=''.join(content))
