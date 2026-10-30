from django.db import models


# Esta classe vira uma TABELA no banco. Cada linha abaixo vira uma COLUNA.
class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    senha = models.CharField(max_length=200)  # guarda a senha criptografada
    habilidadeEnsina = models.CharField(max_length=100)
    habilidadeAprende = models.CharField(max_length=100)
