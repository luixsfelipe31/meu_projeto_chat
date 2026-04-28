

from django.urls import path
from . import views
from django.conf import settings  # Adicione isto
from django.conf.urls.static import static  # Adicione isto

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('chat/', views.chat, name='chat'),
    path('match/', views.match),
    path('chat/<int:user_id>/', views.chat),
    path('enviar/<int:user_id>/', views.enviar_mensagem, name='enviar'),
    path('como-funciona/', views.como_funciona, name='como_funciona'),
]

# ADICIONE ESTAS LINHAS ABAIXO DO urlpatterns
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)