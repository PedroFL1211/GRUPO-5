# Migration inicial das funcionalidades principais do Desenrola.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Habilidade",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=120)),
                ("descricao", models.TextField()),
                ("categoria", models.CharField(max_length=80)),
                ("nivel", models.CharField(choices=[("iniciante", "Iniciante"), ("intermediario", "Intermediário"), ("avancado", "Avançado")], default="iniciante", max_length=20)),
                ("formato", models.CharField(choices=[("online", "Online"), ("presencial", "Presencial")], default="online", max_length=12)),
                ("preco", models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ("disponibilidade", models.TextField(blank=True)),
                ("ativa", models.BooleanField(default=True)),
                ("criada_em", models.DateTimeField(auto_now_add=True)),
                ("mentor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="habilidades", to="usuarios.usuario")),
            ],
        ),
        migrations.CreateModel(
            name="Sessao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("inicio", models.DateTimeField()),
                ("fim", models.DateTimeField()),
                ("status", models.CharField(choices=[("pendente", "Pendente"), ("aceita", "Aceita"), ("recusada", "Recusada"), ("cancelada", "Cancelada"), ("concluida", "Concluída")], default="pendente", max_length=12)),
                ("observacoes", models.TextField(blank=True)),
                ("criada_em", models.DateTimeField(auto_now_add=True)),
                ("aprendiz", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sessoes_como_aprendiz", to="usuarios.usuario")),
                ("habilidade", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sessoes", to="usuarios.habilidade")),
            ],
        ),
        migrations.CreateModel(
            name="Avaliacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nota", models.PositiveSmallIntegerField()),
                ("comentario", models.TextField(blank=True)),
                ("criada_em", models.DateTimeField(auto_now_add=True)),
                ("avaliado", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="avaliacoes_recebidas", to="usuarios.usuario")),
                ("avaliador", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="avaliacoes_feitas", to="usuarios.usuario")),
                ("sessao", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="avaliacoes", to="usuarios.sessao")),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("sessao", "avaliador"), name="avaliacao_unica_por_avaliador_sessao"),
                    models.CheckConstraint(condition=models.Q(("nota__gte", 1), ("nota__lte", 5)), name="avaliacao_nota_entre_1_e_5"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Favorito",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("habilidade", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="favoritada_por", to="usuarios.habilidade")),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="favoritos", to="usuarios.usuario")),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("usuario", "habilidade"), name="favorito_unico_por_usuario"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Denuncia",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("motivo", models.CharField(max_length=120)),
                ("descricao", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("aberta", "Aberta"), ("em_analise", "Em análise"), ("resolvida", "Resolvida")], default="aberta", max_length=12)),
                ("criada_em", models.DateTimeField(auto_now_add=True)),
                ("denunciante", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="denuncias_feitas", to="usuarios.usuario")),
                ("habilidade", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="denuncias", to="usuarios.habilidade")),
                ("usuario_denunciado", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="denuncias_recebidas", to="usuarios.usuario")),
            ],
        ),
    ]
