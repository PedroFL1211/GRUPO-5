from django.contrib import admin
from .models import Usuario, Habilidade, Sessao, Avaliacao, Favorito, Denuncia


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "username", "habilidadeEnsina", "habilidadeAprende")
    search_fields = ("nome", "username")


@admin.register(Habilidade)
class HabilidadeAdmin(admin.ModelAdmin):
    list_display = ("titulo", "mentor", "categoria", "nivel", "formato", "preco", "ativa")
    list_filter = ("categoria", "nivel", "formato", "ativa")
    search_fields = ("titulo", "descricao", "mentor__username")


@admin.register(Sessao)
class SessaoAdmin(admin.ModelAdmin):
    list_display = ("id", "habilidade", "aprendiz", "inicio", "fim", "status")
    list_filter = ("status",)
    search_fields = ("habilidade__titulo", "aprendiz__username")


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "sessao", "avaliador", "avaliado", "nota", "criada_em")
    list_filter = ("nota",)


@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "habilidade", "criado_em")


@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display = ("id", "denunciante", "usuario_denunciado", "habilidade", "status", "criada_em")
    list_filter = ("status",)
    search_fields = ("motivo", "descricao")
