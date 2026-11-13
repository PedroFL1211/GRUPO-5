from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from .models import Usuario, Denuncia, EventoModeracao
from .forms_denuncias import DenunciaForm
from .recomendacoes import recomendar


class ModeracaoTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('moderador', password='teste', is_staff=True)
        self.login = User.objects.create_user('alvo', password='teste')
        self.usuario = Usuario.objects.create(nome='Alvo', username='alvo', senha='hash', habilidadeEnsina='Python, Inglês; Violão', habilidadeAprende='Design')
        self.denuncia = Denuncia.objects.create(tipo='usuario', alvo='@alvo', motivo='Teste', descricao='Relato', usuario_alvo=self.usuario)
        self.painel = reverse('moderacao_denuncias')
        self.status = reverse('moderacao_status', args=[self.denuncia.pk])
        self.remover = reverse('moderacao_remover', args=[self.denuncia.pk])

    def test_acesso_restrito_a_equipe(self):
        for url in [self.painel, self.status, self.remover]:
            self.assertEqual(self.client.get(url).status_code, 302)
            self.client.force_login(self.login)
            self.assertEqual(self.client.post(url).status_code, 403)
            self.client.logout()
        self.client.force_login(self.staff)
        self.assertContains(self.client.get(self.painel), 'Moderação de denúncias')

    def test_status_filtro_e_historico(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(self.status).status_code, 405)
        self.assertEqual(self.client.post(self.status, {'status': 'inventado'}).status_code, 400)
        for status in ['em_analise', 'resolvida', 'aberta']:
            self.assertRedirects(self.client.post(self.status, {'status': status}), self.painel)
            self.denuncia.refresh_from_db()
            self.assertEqual(self.denuncia.status, status)
        self.assertEqual(EventoModeracao.objects.count(), 3)
        self.assertNotContains(self.client.get(self.painel, {'status': 'resolvida'}), '@alvo')
        self.assertContains(self.client.get(self.painel, {'status': 'aberta'}), '@alvo')

    def test_remove_perfil_login_e_preserva_denuncia(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(self.remover).status_code, 405)
        self.assertEqual(self.client.post(self.remover).status_code, 400)
        self.client.post(self.remover, {'confirmar': 'sim'})
        self.assertFalse(Usuario.objects.filter(pk=self.usuario.pk).exists())
        self.assertFalse(User.objects.filter(pk=self.login.pk).exists())
        self.denuncia.refresh_from_db()
        self.assertEqual(self.denuncia.status, 'resolvida')
        self.assertIsNone(self.denuncia.usuario_alvo_id)
        self.assertEqual(self.denuncia.alvo, '@alvo')
        self.assertEqual(self.denuncia.eventos.count(), 1)

    def test_remove_apenas_habilidade_do_alvo_e_atualiza_recomendacoes(self):
        outro = Usuario.objects.create(nome='Outro', username='outro', senha='hash', habilidadeEnsina='Inglês', habilidadeAprende='')
        aprendiz = Usuario.objects.create(nome='Aprendiz', username='aprendiz', senha='hash', habilidadeEnsina='Design', habilidadeAprende='Inglês')
        self.denuncia.tipo = 'habilidade'
        self.denuncia.habilidade_alvo = 'Inglês'
        self.denuncia.save()
        self.client.force_login(self.staff)
        self.client.post(self.remover, {'confirmar': 'sim'})
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.habilidadeEnsina, 'Python, Violão')
        outro.refresh_from_db()
        self.assertEqual(outro.habilidadeEnsina, 'Inglês')
        self.assertTrue(User.objects.filter(pk=self.login.pk).exists())
        resultados = recomendar(aprendiz)
        self.assertNotIn(self.usuario.pk, [item['usuario'].pk for lista in [resultados['troca_perfeita'], resultados['ensinam_voce']] for item in lista])

    def test_protege_moderadores_e_denuncias_antigas(self):
        self.client.force_login(self.staff)
        self.login.is_staff = True
        self.login.save()
        self.client.post(self.remover, {'confirmar': 'sim'})
        self.assertTrue(Usuario.objects.filter(pk=self.usuario.pk).exists())
        self.denuncia.usuario_alvo = None
        self.denuncia.save()
        self.client.post(self.remover, {'confirmar': 'sim'})
        self.assertTrue(User.objects.filter(pk=self.login.pk).exists())
        self.assertEqual(EventoModeracao.objects.count(), 0)

    def test_nova_denuncia_vincula_alvo_e_valida_campos(self):
        self.assertEqual(self.client.post(reverse('reportar'), {'tipo': 'usuario', 'alvo': '@alvo'}).status_code, 200)
        self.assertEqual(Denuncia.objects.count(), 1)
        self.assertRedirects(self.client.post(reverse('reportar'), {'destino': f'u:{self.usuario.pk}', 'motivo': 'Motivo', 'descricao': 'Relato'}), reverse('reportar'))
        nova = Denuncia.objects.latest('pk')
        self.assertEqual(nova.usuario_alvo_id, self.usuario.pk)
        self.assertEqual(nova.status, 'aberta')
        form = DenunciaForm()
        chave = next(chave for chave, (_, habilidade) in form.alvos.items() if habilidade == 'Inglês')
        self.client.post(reverse('reportar'), {'destino': chave, 'motivo': 'Motivo', 'descricao': 'Relato'})
        self.assertEqual(Denuncia.objects.latest('pk').habilidade_alvo, 'Inglês')

    def test_habilidade_alterada_e_denuncia_resolvida_nao_apagam_outros_dados(self):
        self.client.force_login(self.staff)
        self.denuncia.tipo = 'habilidade'
        self.denuncia.habilidade_alvo = 'Habilidade inexistente'
        self.denuncia.save()
        self.client.post(self.remover, {'confirmar': 'sim'})
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.habilidadeEnsina, 'Python, Inglês; Violão')
        self.denuncia.tipo = 'usuario'
        self.denuncia.status = 'resolvida'
        self.denuncia.save()
        self.client.post(self.remover, {'confirmar': 'sim'})
        self.assertTrue(Usuario.objects.filter(pk=self.usuario.pk).exists())

    def test_csrf_e_escape_html(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.staff)
        self.assertEqual(cliente.post(self.remover, {'confirmar': 'sim'}).status_code, 403)
        self.denuncia.descricao = '<script>alert(1)</script>'
        self.denuncia.save()
        resposta = cliente.get(self.painel)
        self.assertContains(resposta, '&lt;script&gt;')
        self.assertNotContains(resposta, '<script>alert(1)</script>')

    def test_home_mostra_link_so_para_equipe(self):
        self.assertNotContains(self.client.get(reverse('home')), self.painel)
        self.client.force_login(self.staff)
        self.assertContains(self.client.get(reverse('home')), self.painel)
