

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Mensagem, Usuario 

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.me = self.scope.get("session", {}).get("usuario_id") or self.scope.get("user").id

        if not self.me:
            print("❌ DEBUG: Usuário não identificado. Fechando socket.")
            await self.close()
            return

        ids = sorted([int(self.me), int(self.user_id)])
        self.room_group_name = f"chat_{ids[0]}_{ids[1]}"
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"✅ CONECTADO! Grupo: {self.room_group_name} | Eu: {self.me}")

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        
        # --- ADICIONADO: SALVAR NO BANCO ---
        if message:
            await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.me,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
        }))

    # --- ADICIONADO: FUNÇÃO PARA GRAVAR NO BANCO ---
    @database_sync_to_async
    def save_message(self, message):
        try:
            remetente = Usuario.objects.get(id=self.me)
            destinatario = Usuario.objects.get(id=self.user_id)
            
            Mensagem.objects.create(
                remetente=remetente,
                destinatario=destinatario,
                texto=message # Verifique se no seu models.py o campo chama 'conteudo'
            )
            print(f"💾 Mensagem salva no banco!")
        except Exception as e:
            print(f"⚠️ Erro ao salvar mensagem: {e}")