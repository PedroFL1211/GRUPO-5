from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

@login_required(login_url='login')
def lista_notificacoes(request):
    notificacoes = request.user.notificacoes.all()
    return render(request, "notificacoes.html", {"notificacoes": notificacoes})

@login_required(login_url='login')
def marcar_lida(request, pk):
    request.user.notificacoes.filter(pk=pk).update(lida=True)
    return redirect("notificacoes")

@login_required(login_url='login')
def marcar_todas_lidas(request):
    request.user.notificacoes.filter(lida=False).update(lida=True)
    return redirect("notificacoes")
