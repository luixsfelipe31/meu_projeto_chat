from django.shortcuts import render, redirect
from .models import Usuario
from django.http import JsonResponse
from .models import Mensagem
from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'usuarios/home.html')

def cadastro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        Usuario.objects.create(
            username=username,
            password=password
        )
        # opcional: mensagem de sucesso
        return render(request, 'usuarios/cadastro.html', {'sucesso': 'Usuário cadastrado com sucesso!'})

    return render(request, 'usuarios/cadastro.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuarios = Usuario.objects.filter(username=username, password=password)

        if usuarios.exists():
            # SALVA O USUÁRIO NA SESSÃO
            request.session['usuario_id'] = usuarios.first().id
            request.session['usuario_nome'] = username
            return redirect('dashboard')  # usa redirect para dashboard
        else:
            return render(request, 'usuarios/login.html', {'erro': 'Usuário inválido'})

    return render(request, 'usuarios/login.html')


def dashboard(request):
    usuario_nome = request.session.get('usuario_nome')  # pega o nome do usuário logado
    if not usuario_nome:
        return redirect('home')  # se não estiver logado, volta pra home
    return render(request, 'usuarios/dashboard.html', {'usuario_nome': usuario_nome})


def logout_view(request):
    request.session.flush()  # limpa sessão
    return redirect('home')


def chat(request, user_id):
    usuario_logado = request.session.get('usuario_nome')

    if not usuario_logado:
        return redirect('home')

    de_usuario = Usuario.objects.filter(username=usuario_logado).first()
    para_usuario = Usuario.objects.get(id=user_id)

    mensagens = Mensagem.objects.filter(
        remetente__in=[de_usuario, para_usuario],
        destinatario__in=[de_usuario, para_usuario]
    ).order_by('criado_em')

    return render(request, 'usuarios/chat.html', {
        'mensagens': mensagens,
        'destinatario': para_usuario
    })




def match(request):
    usuario_logado = request.session.get('usuario_nome')

    if not usuario_logado:
        return redirect('home')

    usuario = Usuario.objects.filter(username=usuario_logado).first()
    
    # 🔥 MOSTRA TODOS MENOS ELE MESMO
    sugestoes = Usuario.objects.exclude(id=usuario.id)

    return render(request, 'usuarios/match.html', {
        'sugestoes': sugestoes
    })

def cadastro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        idioma_nativo = request.POST.get('idioma_nativo')
        idioma_aprendizado = request.POST.get('idioma_aprendizado')
        interesses = request.POST.get('interesses')
        foto = request.FILES.get('foto')  # 🔥 AQUI

        Usuario.objects.create(
            username=username,
            password=password,
            idioma_nativo=idioma_nativo,
            idioma_aprendizado=idioma_aprendizado,
            interesses=interesses,
            foto=foto  # 🔥 AQUI
        )

        return redirect('/login/')

    return render(request, 'usuarios/cadastro.html')

def chat(request, user_id):
    usuario_logado = request.session.get('usuario_nome')

    if not usuario_logado:
        return redirect('home')

    de_usuario = Usuario.objects.filter(username=usuario_logado).first()
    para_usuario = Usuario.objects.get(id=user_id)

    # 🔥 mensagens do chat atual
    mensagens = Mensagem.objects.filter(
        remetente__in=[de_usuario, para_usuario],
        destinatario__in=[de_usuario, para_usuario]
    ).order_by('criado_em')

    # 🔥 LISTA DE CONVERSAS (SIDEBAR)
    conversas = Mensagem.objects.filter(
        remetente=de_usuario
    ).values_list('destinatario', flat=True)

    conversas_recebidas = Mensagem.objects.filter(
        destinatario=de_usuario
    ).values_list('remetente', flat=True)

    usuarios_ids = set(list(conversas) + list(conversas_recebidas))

    usuarios_conversas = Usuario.objects.filter(id__in=usuarios_ids)

    return render(request, 'usuarios/chat.html', {
        'mensagens': mensagens,
        'destinatario': para_usuario,
        'usuarios_conversas': usuarios_conversas
    })


def enviar_mensagem(request, user_id):
    usuario_logado = request.session.get('usuario_nome')

    # 🔥 CORREÇÃO AQUI TAMBÉM
    de_usuario = Usuario.objects.filter(username=usuario_logado).first()
    para_usuario = Usuario.objects.get(id=user_id)

    texto = request.POST.get('texto')

    Mensagem.objects.create(
        remetente=de_usuario,
        destinatario=para_usuario,
        texto=texto
    )

    return JsonResponse({'status': 'ok'})



def como_funciona(request):
    return HttpResponse("FUNCIONOU")