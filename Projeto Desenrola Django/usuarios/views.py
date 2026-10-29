from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Usuario


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


# LISTA: busca todos os usuários no banco
@login_required
def listarUsuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, "usuarios/lista.html", {"usuarios": usuarios})


# EDIÇÃO: mostra os dados atuais e salva as mudanças
@login_required
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
@login_required
def removerUsuario(request, idUsuario):
    usuario = get_object_or_404(Usuario, id=idUsuario)
    if request.method == "POST":
        User.objects.filter(username=usuario.username).delete()  # apaga também o login
        usuario.delete()
    return redirect("/usuarios/")
