from django.shortcuts import render, redirect
from .models import Usuario
from django.http import JsonResponse
from .models import Mensagem
from django.shortcuts import render
from django.http import HttpResponse
import unicodedata


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
        print("POST:", request.POST)

        username = request.POST.get('username').strip()
        password = request.POST.get('senha').strip()

        usuarios = Usuario.objects.filter(username=username, password=password)

        print("ENCONTRADOS:", usuarios)  # DEBUG

        if usuarios.exists():
            user = usuarios.first()

            request.session['usuario_id'] = user.id
            request.session['usuario_nome'] = user.username

            print("LOGIN OK")  # DEBUG

            return redirect('dashboard')
        else:
            print("LOGIN FALHOU")  # DEBUG
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

    # Segurança: Redireciona se não estiver logado
    if not usuario_logado:
        return redirect('home')

    user = Usuario.objects.filter(username=usuario_logado).first()
    
    # Se por algum motivo o user não existir no banco
    if not user:
        return redirect('home')

    outros = Usuario.objects.exclude(id=user.id)
    sugestoes = []

    # 1. Prepara os interesses do usuário logado (limpos e sem acento)
    # Criamos um SET para comparação ultra rápida
    meus_interesses = set(
        normalizar_texto(i) for i in user.interesses.split(',') if i.strip()
    )

    for outro in outros:
        score = 0
        
        # --- 🎯 MATCH DE IDIOMA (Peso 40 cada) ---
        if user.idioma_nativo == outro.idioma_aprendizado: 
            score += 40
        if user.idioma_aprendizado == outro.idioma_nativo: 
            score += 40

        # --- 🎯 MATCH DE INTERESSES (Normalizado) ---
        outro.interesses_comuns = [] # Inicializa lista vazia
        if outro.interesses:
            interesses_outro = set(
                normalizar_texto(i) for i in outro.interesses.split(',') if i.strip()
            )

            # Interseção: O que os dois têm igual
            comuns = meus_interesses.intersection(interesses_outro)
            
            # Adiciona 15 pontos para cada hobby em comum
            score += len(comuns) * 15
            
            # Guardamos para mostrar no HTML (opcional)
            outro.interesses_comuns = list(comuns)

        # Atribui o score final limitado a 100%
        outro.score = min(score, 100)
        sugestoes.append(outro)

    # 🔥 ORDENAÇÃO: Os melhores matches primeiro
    sugestoes.sort(key=lambda x: x.score, reverse=True)

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


def normalizar_texto(texto):
    if not texto:
        return ""
    # Remove acentos e caracteres especiais (ex: 'á' vira 'a')
    texto_norm = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    # Remove espaços sobrando e deixa tudo minusculo
    return texto_norm.strip().lower()