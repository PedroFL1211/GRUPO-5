from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from .models import Usuario


# LOGIN: confere usuário e senha no banco
def telaLogin(request):
    erro = ""
    if request.method == "POST":
        usuario = Usuario.objects.filter(username=request.POST["username"]).first()
        if usuario is not None and check_password(request.POST["password"], usuario.senha):
            return redirect("/usuarios/")
        erro = "Usuário ou senha incorretos"
    return render(request, "usuarios/login.html", {"erro": erro})


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
            return redirect("/usuarios/")
    return render(request, "usuarios/cadastro.html", {"erro": erro})


# LISTA: busca todos os usuários no banco
def listarUsuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, "usuarios/lista.html", {"usuarios": usuarios})


# EDIÇÃO: mostra os dados atuais e salva as mudanças
def editarUsuario(request, idUsuario):
    usuario = get_object_or_404(Usuario, id=idUsuario)
    if request.method == "POST":
        usuario.nome = request.POST["nome"]
        usuario.habilidadeEnsina = request.POST["ensina"]
        usuario.habilidadeAprende = request.POST["aprende"]
        usuario.save()
        return redirect("/usuarios/")
    return render(request, "usuarios/editar.html", {"usuario": usuario})


# REMOÇÃO: apaga o usuário do banco
def removerUsuario(request, idUsuario):
    usuario = get_object_or_404(Usuario, id=idUsuario)
    if request.method == "POST":
        usuario.delete()
    return redirect("/usuarios/")
