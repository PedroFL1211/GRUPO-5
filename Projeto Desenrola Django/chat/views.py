from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from .forms import MensagemForm
from .models import Mensagem

@login_required(login_url='login')
@require_http_methods(["GET"])
def lista(request):
    usuarios = get_user_model().objects.filter(is_active=True).exclude(pk=request.user.pk).order_by("username")
    return render(request, "chat/lista.html", {"usuarios":usuarios})

@login_required
@require_http_methods(["GET", "POST"])
def conversa(request, usuario_id):
    outro = get_object_or_404(get_user_model(), pk=usuario_id, is_active=True)
    if outro.pk == request.user.pk:
        raise Http404("Escolha outro usuário.")
    form = MensagemForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        Mensagem.objects.create(remetente=request.user, destinatario=outro, texto=form.cleaned_data["texto"])
        return redirect("chat:conversa", usuario_id=outro.pk)
    # A consulta sempre inclui o usuário autenticado: não expõe conversas de terceiros.
    mensagens = Mensagem.objects.filter(Q(remetente=request.user, destinatario=outro) | Q(remetente=outro, destinatario=request.user)).select_related("remetente")
    # Exibe as 100 mais recentes em ordem cronológica.
    mensagens = list(mensagens.order_by("-criada_em", "-pk")[:100])[::-1]
    return render(request, "chat/conversa.html", {"outro":outro, "mensagens":mensagens, "form":form})
