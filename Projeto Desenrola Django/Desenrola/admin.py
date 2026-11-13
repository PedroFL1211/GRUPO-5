from django.contrib import admin
from .models import Denuncia, Usuario

admin.site.register(Denuncia)
admin.site.register(Usuario)
from .models import Notificacao

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "tipo", "mensagem", "lida", "criada_em")
    list_filter = ("tipo", "lida")
