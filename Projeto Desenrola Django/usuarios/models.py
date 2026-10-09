from django.db import models


class Usuario(models.Model):
    # Perfil base: um usuário pode ensinar e aprender.
    nome = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    senha = models.CharField(max_length=200)  # senha armazenada com hash
    habilidadeEnsina = models.CharField(max_length=100)
    habilidadeAprende = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Habilidade(models.Model):
    class Nivel(models.TextChoices):
        INICIANTE = "iniciante", "Iniciante"
        INTERMEDIARIO = "intermediario", "Intermediário"
        AVANCADO = "avancado", "Avançado"

    class Formato(models.TextChoices):
        ONLINE = "online", "Online"
        PRESENCIAL = "presencial", "Presencial"

    mentor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="habilidades")
    titulo = models.CharField(max_length=120)
    descricao = models.TextField()
    categoria = models.CharField(max_length=80)
    nivel = models.CharField(max_length=20, choices=Nivel.choices, default=Nivel.INICIANTE)
    formato = models.CharField(max_length=12, choices=Formato.choices, default=Formato.ONLINE)
    preco = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    disponibilidade = models.TextField(blank=True)
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class Sessao(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        ACEITA = "aceita", "Aceita"
        RECUSADA = "recusada", "Recusada"
        CANCELADA = "cancelada", "Cancelada"
        CONCLUIDA = "concluida", "Concluída"

    habilidade = models.ForeignKey(Habilidade, on_delete=models.CASCADE, related_name="sessoes")
    aprendiz = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="sessoes_como_aprendiz")
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDENTE)
    observacoes = models.TextField(blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.habilidade.titulo} - {self.inicio:%d/%m/%Y %H:%M}"


class Avaliacao(models.Model):
    sessao = models.ForeignKey(Sessao, on_delete=models.CASCADE, related_name="avaliacoes")
    avaliador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="avaliacoes_feitas")
    avaliado = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="avaliacoes_recebidas")
    nota = models.PositiveSmallIntegerField()
    comentario = models.TextField(blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["sessao", "avaliador"], name="avaliacao_unica_por_avaliador_sessao"),
            models.CheckConstraint(condition=models.Q(nota__gte=1, nota__lte=5), name="avaliacao_nota_entre_1_e_5"),
        ]

    def __str__(self):
        return f"Avaliação {self.nota}/5 - {self.avaliado}"


class Favorito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="favoritos")
    habilidade = models.ForeignKey(Habilidade, on_delete=models.CASCADE, related_name="favoritada_por")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["usuario", "habilidade"], name="favorito_unico_por_usuario"),
        ]

    def __str__(self):
        return f"{self.usuario} favoritou {self.habilidade}"


class Denuncia(models.Model):
    class Status(models.TextChoices):
        ABERTA = "aberta", "Aberta"
        EM_ANALISE = "em_analise", "Em análise"
        RESOLVIDA = "resolvida", "Resolvida"

    denunciante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="denuncias_feitas")
    usuario_denunciado = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="denuncias_recebidas",
        null=True, blank=True
    )
    habilidade = models.ForeignKey(
        Habilidade, on_delete=models.CASCADE, related_name="denuncias",
        null=True, blank=True
    )
    motivo = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ABERTA)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Denúncia #{self.pk} - {self.motivo}"
