import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.me = None
        self.room_group_name = None

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        
        # Chamamos uma função separada para pegar os dados de forma segura
        self.me = await self.get_user_session()

        # Se não logado, aborta
        if not self.me:
            print("DEBUG: Usuário não autenticado.")
            await self.close()
            return

        # Define o grupo
        ids = sorted([int(self.me), int(self.user_id)])
        self.room_group_name = f"chat_{ids[0]}_{ids[1]}"
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"✅ CONECTADO! Grupo: {self.room_group_name}")

    # Esta função resolve o erro "Async context"
    @database_sync_to_async
    def get_user_session(self):
        # AQUI você acessa a sessão ou o banco de forma segura
        sessao = self.scope.get("session")
        return sessao.get("usuario_id")

    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # 1. Quando o navegador envia algo, você recebe aqui e manda para o grupo
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        
        print(f"DEBUG: Recebido do front: {message}") # Deve aparecer no seu terminal Daphne

        # A MÁGICA: Manda para todo mundo no grupo (incluindo você mesmo)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.me,
            }
        )

    # 2. Quando o grupo envia algo, o servidor chama este método para cada pessoa conectada
    async def chat_message(self, event):
        # Envia de volta para o JavaScript do navegador
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
        }))