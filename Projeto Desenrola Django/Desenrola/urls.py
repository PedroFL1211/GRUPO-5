"""
URL configuration for Desenrola project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views_recomendacoes
from . import views
from . import views_moderacao
from . import views_notificacoes
from django.contrib.auth import urls as auth_urls
from django.urls import include

urlpatterns = [
    path('accounts/', include(auth_urls)),
    path('chat/', include('chat.urls')),
    path('moderacao/denuncias/', views_moderacao.painel, name='moderacao_denuncias'),
    path('moderacao/denuncias/<int:pk>/status/', views_moderacao.alterar_status, name='moderacao_status'),
    path('moderacao/denuncias/<int:pk>/remover/', views_moderacao.remover_alvo, name='moderacao_remover'),
    path('', views.home, name='home'),
    path("admin/", admin.site.urls),
    path("recomendacoes/", views_recomendacoes.recomendacoes, name="recomendacoes"),
    path('perfil/', views.meu_perfil_view, name='meu_perfil'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),
    path('perfil/<str:username>/', views.perfil_publico, name='perfil_publico'),
    path('sessoes/', views.sessoes_view, name='sessoes'),
    path('notificacoes/', views_notificacoes.lista_notificacoes, name='notificacoes'),
    path('notificacoes/todas-lidas/', views_notificacoes.marcar_todas_lidas, name='marcar_todas_lidas'),
    path('notificacoes/<int:pk>/lida/', views_notificacoes.marcar_lida, name='marcar_lida'),
    path('404/', views.erro404, name='erro404'),
    path('denunciar/', views.reportar, name='reportar'),
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('excluir-conta/', views.excluir_conta_view, name='excluir_conta'),
    path('logout/', views.sair_view, name='logout'),
]
