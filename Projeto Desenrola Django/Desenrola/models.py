from django.db import models
from django.contrib.auth.models import User

class Denuncia(models.Model):
    TIPO_CHOICES = [
        ('usuario', 'Usuário'),
        ('habilidade', 'Habilidade'),
    ]
    
    STATUS_CHOICES = [('aberta', 'Aberta'), ('em_analise', 'Em análise'), ('resolvida', 'Resolvida')]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    usuario_alvo = models.ForeignKey('Usuario', null=True, blank=True, on_delete=models.SET_NULL, related_name='denuncias')
    habilidade_alvo = models.CharField(max_length=100, blank=True)

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    alvo = models.CharField(max_length=100)
    motivo = models.CharField(max_length=150)
    descricao = models.TextField()
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo.capitalize()}: {self.alvo}"

class Usuario(models.Model):
    FORMATO_CHOICES = [
        ('Presencial', 'Presencial'),
        ('Online', 'Online'),
        ('Flexível', 'Flexível'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    nome = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    bio = models.TextField(max_length=200)
    formato_troca = models.CharField(max_length=20, choices=FORMATO_CHOICES, default='Flexível')
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
    @property
    def habilidadeEnsina(self):
        return ", ".join(self.habilidades.filter(tipo="ensinar").values_list("nome", flat=True))

    @property
    def habilidadeAprende(self):
        return ", ".join(self.habilidades.filter(tipo="aprender").values_list("nome", flat=True))
        
class Habilidade(models.Model):
    TIPO_CHOICES = [
        ('ensinar', 'Posso Ensinar'),
        ('aprender', 'Quero Aprender'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='habilidades')
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return f"{self.nome} ({self.tipo})"
      
class EventoModeracao(models.Model):
    denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE, related_name='eventos')
    moderador = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL)
    descricao = models.CharField(max_length=250)
    criado_em = models.DateTimeField(auto_now_add=True)

class Notificacao(models.Model):
    TIPOS = [
        ("nova_solicitacao", "Nova solicitação"),
        ("sessao_aceita", "Sessão aceita"),
        ("sessao_recusada", "Sessão recusada"),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificacoes")
    tipo = models.CharField(max_length=30, choices=TIPOS)
    mensagem = models.CharField(max_length=255)
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criada_em"]

    def __str__(self):
        return f"{self.get_tipo_display()} para {self.usuario}"

class Favorito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='favoritos')
    habilidade = models.ForeignKey(Habilidade, on_delete=models.CASCADE, related_name='favoritada_por')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'habilidade'], name='um_favorito_por_habilidade'),
        ]

    def __str__(self):
        return f"{self.usuario} favoritou {self.habilidade.nome}"

class Sessao(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]

    FORMATO_CHOICES = [
        ('Online', 'Online'),
        ('Presencial', 'Presencial'),
    ]

    solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sessoes_solicitadas')
    convidado = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sessoes_recebidas')
    habilidade = models.CharField(max_length=100)
    data_hora = models.DateTimeField()
    formato = models.CharField(max_length=20, choices=FORMATO_CHOICES, default='Online')
    local_ou_link = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_hora']

    def __str__(self):
        return f"{self.habilidade} ({self.solicitante.nome} ↔ {self.convidado.nome}) - {self.status}"