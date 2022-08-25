import json
import requests
from channels.generic.websocket import AsyncJsonWebsocketConsumer

connection_list = {}


class SocketAdapter(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_tasks = set()
        self.connected = False

    async def connect(self):
        self.connected = True
        await self.accept()

    async def disconnect(self, close_code):
        self.connected = False
        print('-----socket disconnected-----')

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        request = json.loads(text_data)
        method = request.get("method", None)
        params = request.get("params", None)
        fields = {}
        if 'fields' in params:
            fields = params['fields']
        id = request.get("id", None)

        if method == 'setupTrigger':
            path = fields["webhook_url"].strip("/").split("/")[-1]
            connection_list[path] = self
            response = {
                'jsonrpc': '2.0',
                'result': {},
                'id': id
            }
            await self.send_json(response)

        if method == 'callWebhook':
            path = fields["path"]
            existed = next((i for i, d in enumerate(connection_list) if path in d), None)
            if existed:
                run_action_response = {
                    'jsonrpc': '2.0',
                    'result': {
                        'key': 'notifySignal',
                        'payload': params
                    },
                    'id': id
                }
                await connection_list[existed].send_json(run_action_response)
            response = {
                'jsonrpc': '2.0',
                'result': {},
                'id': id
            }
            await self.send_json(response)

        if method == 'runAction':
            request_method = ""
            request_url = ""
            request_data = ""
            if "method" in fields:
                request_method = fields['method']
            if "url" in fields:
                request_url = fields['url']
            if "data" in fields:
                if fields['data'] != "":
                    request_data = json.loads(fields['data'])

            if request_method == "GET":
                r = requests.get(url=request_url, params=request_data)
            if request_method == "POST":
                r = requests.post(url=request_url, data=request_data)
            if request_method == "PUT":
                r = requests.put(url=request_url, data=request_data)
            if request_method == "PATCH":
                r = requests.patch(url=request_url, data=request_data)
            if request_method == "DELETE":
                r = requests.delete(url=request_url, data=request_data)
            result = r.json()
            print('---------------------------', result.status_code)

            response = {
                'jsonrpc': '2.0',
                'result': {result.status_code},
                'id': id
            }
            await self.send_json(response)

        if method == 'ping':
            response = {
                'jsonrpc': '2.0',
                'result': {},
                'id': id
            }
            await self.send_json(response)
