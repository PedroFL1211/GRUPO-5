from .models import Notificacao

def notificar(usuario, tipo, mensagem):
    Notificacao.objects.create(usuario=usuario, tipo=tipo, mensagem=mensagem)
