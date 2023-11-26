import json
import asyncio
import uuid

from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    update_lock = asyncio.Lock()
    players = {}

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        self.player_id = str(uuid.uuid4())
        self.players[self.player_id] = {'id': self.player_id}

        if len(self.players) == 1:
            asyncio.create_task(self.game_loop())


    async def disconnect(self, close_code):
        async with self.update_lock:
            if self.player_id in self.players:
                del self.players[self.player_id]
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.room_group_name, {'type': 'chat_message', 'message': message}
        )

    # Custom functions after here
    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))

    async def game_loop(self):
        total_time = 0
        while len(self.players) > 0:
            async with self.update_lock:
                pass
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {'type': 'chat_message', 'message': f'Time: {total_time}'}
                    )
            await asyncio.sleep(1)
            total_time += 1
