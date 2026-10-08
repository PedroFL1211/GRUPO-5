from django.urls import path
from usuarios import views

# Cada rota liga um endereço a uma view
urlpatterns = [
    path("", views.telaLogin),
    path("cadastro/", views.cadastrarUsuario),
    path("usuarios/", views.listarUsuarios),
    path("usuarios/<int:idUsuario>/editar/", views.editarUsuario),
    path("usuarios/<int:idUsuario>/remover/", views.removerUsuario),
]
