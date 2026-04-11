from django.contrib import admin
from .models import Usuario  # importa o modelo que você quer gerenciar

# registra o modelo para aparecer no admin
admin.site.register(Usuario)