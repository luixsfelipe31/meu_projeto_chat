from django.db import models

class Usuario(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    idioma_nativo = models.CharField(max_length=50)
    idioma_aprendizado = models.CharField(max_length=50)
    interesses = models.CharField(max_length=200)

    foto = models.ImageField(upload_to='fotos/', blank=True, null=True)

    def __str__(self):
        return self.username


# 🔥 NOVO MODEL (ADICIONA AQUI)
class Like(models.Model):
    de_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='likes_enviados')
    para_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='likes_recebidos')

    def __str__(self):
        return f"{self.de_usuario} -> {self.para_usuario}"
    
class Mensagem(models.Model):
    remetente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    destinatario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensagens_recebidas')
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='enviada')

    def __str__(self):
        return f"{self.remetente} -> {self.destinatario}"
    status = models.CharField(
    max_length=20,
    default='enviada'
)