from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('chat/', views.chat, name='chat'),
    path('match/', views.match),
    path('chat/<int:user_id>/', views.chat),
    path('enviar/<int:user_id>/', views.enviar_mensagem),
    path('como-funciona/', views.como_funciona, name='como_funciona'),
]