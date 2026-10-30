from django.urls import path, include
from usuarios import views

# Cada rota liga um endereço a uma view
urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),  # login e logout prontos do Django
    path("cadastro/", views.cadastrarUsuario),
    path("usuarios/", views.listarUsuarios),
    path("usuarios/<int:idUsuario>/editar/", views.editarUsuario),
    path("usuarios/<int:idUsuario>/remover/", views.removerUsuario),
]
