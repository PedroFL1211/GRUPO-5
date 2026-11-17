from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Favorito, Habilidade, Usuario


def criar_usuario(nome, login):
    user = User.objects.create_user(login, password='teste')
    return Usuario.objects.create(user=user, nome=nome)


class FavoritasTests(TestCase):
    def setUp(self):
        self.ana = criar_usuario('Ana Souza', 'ana@teste.com')
        self.bruno = criar_usuario('Bruno Lima', 'bruno@teste.com')
        self.violao = Habilidade.objects.create(usuario=self.bruno, nome='Violão', tipo='ensinar')
        self.ingles = Habilidade.objects.create(usuario=self.ana, nome='Inglês', tipo='ensinar')
        self.quer_python = Habilidade.objects.create(usuario=self.bruno, nome='Python', tipo='aprender')
        self.client.force_login(self.ana.user)

    def alternar(self, habilidade):
        return self.client.post(reverse('alternar_favorito', args=[habilidade.pk]))

    def test_favoritar_e_desfavoritar(self):
        self.alternar(self.violao)
        self.assertEqual(Favorito.objects.filter(usuario=self.ana, habilidade=self.violao).count(), 1)
        self.alternar(self.violao)
        self.assertEqual(Favorito.objects.count(), 0)

    def test_nao_favorita_a_propria_habilidade_nem_as_de_aprender(self):
        self.alternar(self.ingles)
        self.assertEqual(self.alternar(self.quer_python).status_code, 404)
        self.assertEqual(Favorito.objects.count(), 0)

    def test_lista_mostra_so_habilidades_de_outras_pessoas_que_ensinam(self):
        pagina = self.client.get(reverse('lista_habilidades'))
        self.assertContains(pagina, 'Violão')
        self.assertNotContains(pagina, 'Inglês')   # a própria
        self.assertNotContains(pagina, 'Python')   # é de "aprender"
        self.assertContains(pagina, '☆ Favoritar')

    def test_tela_de_favoritas_lista_so_os_cards_salvos_pelo_usuario(self):
        self.assertContains(self.client.get(reverse('habilidades_favoritas')), 'ainda não favoritou')
        self.alternar(self.violao)
        pagina = self.client.get(reverse('habilidades_favoritas'))
        self.assertContains(pagina, 'Violão')
        self.assertContains(pagina, '★ Favoritada')
        # outra pessoa não vê os favoritos da Ana
        self.client.force_login(self.bruno.user)
        self.assertNotContains(self.client.get(reverse('habilidades_favoritas')), 'Violão')

    def test_exige_login_e_metodo_post(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('habilidades_favoritas')).status_code, 302)
        self.assertEqual(self.client.post(reverse('alternar_favorito', args=[self.violao.pk])).status_code, 302)
        self.client.force_login(self.ana.user)
        self.assertEqual(self.client.get(reverse('alternar_favorito', args=[self.violao.pk])).status_code, 405)

    def test_volta_para_a_pagina_de_origem_e_ignora_link_externo(self):
        url = reverse('alternar_favorito', args=[self.violao.pk])
        r = self.client.post(url, {'next': reverse('habilidades_favoritas')})
        self.assertRedirects(r, reverse('habilidades_favoritas'))
        r = self.client.post(url, {'next': 'https://site-malicioso.com/'})
        self.assertRedirects(r, reverse('lista_habilidades'))

    def test_usuario_sem_perfil_abre_as_telas_sem_erro(self):
        sem_perfil = User.objects.create_user('semperfil@teste.com', password='teste')
        self.client.force_login(sem_perfil)
        for nome in ['lista_habilidades', 'habilidades_favoritas']:
            self.assertEqual(self.client.get(reverse(nome)).status_code, 200)
