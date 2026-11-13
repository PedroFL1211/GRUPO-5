from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Usuario
from .recomendacoes import recomendar


# RECOMENDAÇÕES: sugere pessoas para trocar habilidades com o usuário logado
@login_required
def recomendacoes(request):
    # O login do Django e o Usuario do Desenrola compartilham o mesmo username
    usuario = Usuario.objects.filter(user=request.user).first()

    contexto = {"usuario": usuario}
    if usuario is not None:
        resultado = recomendar(usuario)
        contexto.update(resultado)
        contexto["total"] = sum(len(v) for v in resultado.values())
    return render(request, "recomendacoes/recomendacoes.html", contexto)
