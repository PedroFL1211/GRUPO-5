from functools import wraps
import re
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Denuncia, EventoModeracao, Usuario
from .recomendacoes import normalizar, separar_habilidades


def moderador(view):
    @login_required
    @wraps(view)
    def protegida(request, *args, **kwargs):
        if not request.user.is_active or not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return protegida


@moderador
def painel(request):
    status = request.GET.get('status', '')
    denuncias = Denuncia.objects.select_related('usuario_alvo').prefetch_related('eventos__moderador').order_by('-data_registro', '-pk')
    if status in dict(Denuncia.STATUS_CHOICES):
        denuncias = denuncias.filter(status=status)
    else:
        status = ''
    pagina = Paginator(denuncias, 20).get_page(request.GET.get('page'))
    return render(request, 'moderacao/painel.html', {'pagina': pagina, 'status': status, 'status_choices': Denuncia.STATUS_CHOICES})


@moderador
@require_POST
@transaction.atomic
def alterar_status(request, pk):
    denuncia = get_object_or_404(Denuncia.objects.select_for_update(), pk=pk)
    status = request.POST.get('status')
    if status not in dict(Denuncia.STATUS_CHOICES):
        return HttpResponseBadRequest('Status inválido.')
    if denuncia.status != status:
        anterior = denuncia.get_status_display()
        denuncia.status = status
        denuncia.save(update_fields=['status'])
        EventoModeracao.objects.create(denuncia=denuncia, moderador=request.user, descricao=f'Status: {anterior} → {denuncia.get_status_display()}')
    messages.success(request, 'Status atualizado.')
    return redirect('moderacao_denuncias')


@moderador
@require_POST
@transaction.atomic
def remover_alvo(request, pk):
    denuncia = get_object_or_404(Denuncia.objects.select_for_update(), pk=pk)
    if request.POST.get('confirmar') != 'sim':
        return HttpResponseBadRequest('Confirme a remoção.')
    if denuncia.status == 'resolvida':
        messages.error(request, 'Esta denúncia já foi resolvida.')
        return redirect('moderacao_denuncias')
    usuario = Usuario.objects.select_for_update().filter(pk=denuncia.usuario_alvo_id).first()
    if usuario is None:
        messages.error(request, 'Alvo sem vínculo ou já removido. Nenhum registro foi alterado.')
        return redirect('moderacao_denuncias')
    if denuncia.tipo == 'usuario':
        login = User.objects.select_for_update().filter(pk=usuario.user_id).first()
        if login and (login.pk == request.user.pk or login.is_staff or login.is_superuser):
            messages.error(request, 'Contas de moderação não podem ser removidas por este painel.')
            return redirect('moderacao_denuncias')
        username = login.username if login else usuario.nome
        descricao = f'Usuário @{username} removido.'
        # O perfil Usuario referencia diretamente a conta auth.User por user.
        if login:
            login.delete()
        usuario.delete()
    elif denuncia.tipo == 'habilidade' and denuncia.habilidade_alvo:
        chave = normalizar(denuncia.habilidade_alvo)
        if chave not in separar_habilidades(usuario.habilidadeEnsina):
            messages.error(request, 'A habilidade denunciada não está mais cadastrada para este usuário.')
            return redirect('moderacao_denuncias')
        partes = re.split(r'[,;/]', usuario.habilidadeEnsina)
        usuario.habilidadeEnsina = ', '.join(parte.strip() for parte in partes if parte.strip() and normalizar(parte) != chave)
        usuario.save(update_fields=['habilidadeEnsina'])
        descricao = f'Habilidade {denuncia.habilidade_alvo} removida de @{usuario.user.username if usuario.user_id else usuario.nome}.'
    else:
        return HttpResponseBadRequest('Alvo inválido.')
    denuncia.status = 'resolvida'
    denuncia.save(update_fields=['status'])
    EventoModeracao.objects.create(denuncia=denuncia, moderador=request.user, descricao=descricao)
    messages.success(request, descricao)
    return redirect('moderacao_denuncias')
