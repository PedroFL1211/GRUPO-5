from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Usuario, Habilidade
from django.contrib import messages
from .models import Denuncia


# CADASTRO: salva um usuário novo no banco
def cadastrarUsuario(request):
    erro = ""
    if request.method == "POST":
        if Usuario.objects.filter(username=request.POST["username"]).exists():
            erro = "Esse usuário já existe"
        else:
            Usuario.objects.create(
                nome=request.POST["nome"],
                username=request.POST["username"],
                senha=make_password(request.POST["password"]),
                habilidadeEnsina=request.POST["ensina"],
                habilidadeAprende=request.POST["aprende"],
            )
            # Cria também o login do Django, com o mesmo username
            user = User(username=request.POST["username"])
            user.set_password(request.POST["password"])
            user.save()
            return redirect("/usuarios/")
    return render(request, "usuarios/cadastro.html", {"erro": erro})

def meu_perfil(request):
    return render(request, 'perfil.html')

def editar_perfil(request):
    return render(request, 'editar.html')

def minhas_sessoes(request):
    return render(request, 'sessoes.html')

def erro404(request):
    return render(request, 'erro404.html')

def home(request):
    return render(request, 'home.html')    

def reportar(request):
    from .forms_denuncias import DenunciaForm
    form = DenunciaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Sua denúncia foi registrada e será analisada pela equipe.')
        return redirect('reportar')
    return render(request, 'denuncia.html', {'form': form})

# PERFIL PÚBLICO
# Dados de EXEMPLO. Quando os models Habilidade e Avaliacao existirem,
# estes dicionários são trocados por consultas ao banco.
PERFIS_EXEMPLO = {
    "marina": {
        "nome": "Marina Costa",
        "iniciais": "MC",
        "cidade": "São Paulo, SP",
        "bio": "Estudante de Design que ama música e artesanato. Topa trocar ideia sobre qualquer coisa criativa!",
        "trocas": 23,
        "habilidades": [
            {"nome": "Fotografia analógica", "categoria": "Artes e Criatividade", "formato": "Presencial"},
            {"nome": "Desenho", "categoria": "Artes e Criatividade", "formato": "Online"},
            {"nome": "Violão", "categoria": "Música", "formato": "Online"},
            {"nome": "Design gráfico", "categoria": "Artes e Criatividade", "formato": "Online"},
        ],
        "avaliacoes": [
            {"autor": "Thiago Mendes", "nota": 5, "habilidade": "Violão", "data": "02/11/2026",
             "texto": "Aula super paciente e bem organizada. Saí tocando minha primeira música."},
            {"autor": "Júlia Ramos", "nota": 5, "habilidade": "Fotografia analógica", "data": "25/10/2026",
             "texto": "Marina explica de um jeito muito claro e ainda trouxe a câmera para eu testar."},
            {"autor": "Carlos Lima", "nota": 4, "habilidade": "Desenho", "data": "10/10/2026",
             "texto": "Ótima troca! Só começamos um pouco atrasados, mas o conteúdo foi excelente."},
        ],
    },
    "thiago": {
        "nome": "Thiago Mendes",
        "iniciais": "TM",
        "cidade": "Rio de Janeiro, RJ",
        "bio": "Professor de inglês nas horas vagas. Quero aprender violão e tocar numa roda de amigos.",
        "trocas": 11,
        "habilidades": [
            {"nome": "Inglês (conversação)", "categoria": "Idiomas", "formato": "Online"},
            {"nome": "Preparação para entrevistas", "categoria": "Desenvolvimento Pessoal", "formato": "Online"},
        ],
        "avaliacoes": [
            {"autor": "Marina Costa", "nota": 5, "habilidade": "Inglês (conversação)", "data": "30/10/2026",
             "texto": "Conversamos o tempo todo em inglês e eu me senti à vontade para errar."},
        ],
    },
}
 
 
def perfil_publico(request, username):
    perfil = PERFIS_EXEMPLO.get(username.lower())
    if perfil is None:
        raise Http404("Perfil não encontrado")
 
    avaliacoes = perfil["avaliacoes"]
    for av in avaliacoes:
        av["estrelas"] = "★" * av["nota"] + "☆" * (5 - av["nota"])
 
    quantidade = len(avaliacoes)
    media = sum(av["nota"] for av in avaliacoes) / quantidade if quantidade else None
 
    contexto = {
        "perfil": perfil,
        "primeiro_nome": perfil["nome"].split()[0],
        "username": username.lower(),
        "avaliacoes": avaliacoes,
        "quantidade": quantidade,
        "media": media,
    }
    return render(request, "perfil_publico.html", contexto)

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        user = authenticate(request, username=email, password=senha)
        
        if user is not None:
            login(request, user)
            return redirect('meu_perfil')
        else:
            messages.error(request, 'E-mail ou senha incorretos.')
            return redirect('login')

    return render(request, 'login.html')

def cadastro_view(request):
    erro = None
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        # 1. Verifica se o e-mail (que usamos como username) já existe no banco
        if User.objects.filter(username=email).exists():
            erro = "Este e-mail já está cadastrado. Tente fazer login."
        else:
            # 2. Se não existir, cria o usuário normalmente
            user = User.objects.create_user(username=email, email=email, password=senha)
            Usuario.objects.create(user=user, nome=nome)
            
            # 3. Faz o login e redireciona para a home
            login(request, user)
            return redirect('home')
            
    # Se houver erro ou for o primeiro acesso, renderiza a página de cadastro passando a variável de erro
    return render(request, 'cadastro.html', {'erro': erro})

@login_required(login_url='login')
def meu_perfil_view(request):
    try:
        perfil = request.user.usuario
    except Usuario.DoesNotExist:
        perfil = Usuario.objects.create(user=request.user, nome=request.user.username)
        
    hab_ensinar = perfil.habilidades.filter(tipo='ensinar')
    hab_aprender = perfil.habilidades.filter(tipo='aprender')
        
    return render(request, 'perfil.html', {
        'perfil': perfil,
        'hab_ensinar': hab_ensinar,
        'hab_aprender': hab_aprender
    })

@login_required(login_url='login')
@login_required(login_url='login')
def editar_perfil_view(request):
    try:
        perfil = request.user.usuario
    except Usuario.DoesNotExist:
        perfil = Usuario.objects.create(user=request.user, nome=request.user.username)
        
    hab_ensinar = perfil.habilidades.filter(tipo='ensinar')
    hab_aprender = perfil.habilidades.filter(tipo='aprender')
    
    if request.method == 'POST':
        if 'salvar_perfil' in request.POST:
            # 1. Salva os dados de texto
            perfil.nome = request.POST.get('nome')
            perfil.cidade = request.POST.get('cidade')
            perfil.bio = request.POST.get('bio')
            perfil.formato_troca = request.POST.get('formato_troca')
            perfil.save()
            
            # 2. Limpa as habilidades antigas e salva as novas baseadas na tela
            perfil.habilidades.all().delete()
            
            # Recupera as listas geradas pelo JavaScript
            lista_ensinar = request.POST.getlist('hab_ensinar[]')
            for nome_hab in lista_ensinar:
                if nome_hab.strip():
                    Habilidade.objects.create(usuario=perfil, nome=nome_hab.strip(), tipo='ensinar')
                    
            lista_aprender = request.POST.getlist('hab_aprender[]')
            for nome_hab in lista_aprender:
                if nome_hab.strip():
                    Habilidade.objects.create(usuario=perfil, nome=nome_hab.strip(), tipo='aprender')
            
            return redirect('meu_perfil')
            
    return render(request, 'editar.html', {
        'perfil': perfil,
        'hab_ensinar': hab_ensinar,
        'hab_aprender': hab_aprender
    })

@login_required(login_url='login')
def sessoes_view(request):
    return render(request, 'sessoes.html')

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required(login_url='login')
def excluir_conta_view(request):
    erro = None
    if request.method == 'POST':
        senha_digitada = request.POST.get('senha')
        user = request.user
        
        if user.check_password(senha_digitada):
            logout(request) # 1º Encerra a sessão e limpa os tokens
            user.delete()   # 2º Apaga o usuário do banco
            return redirect('home')
        else:
            erro = "Senha incorreta. Tente novamente."
            
    return render(request, 'remocao.html', {'erro': erro})

def sair_view(request):
    logout(request)
    return redirect('home')