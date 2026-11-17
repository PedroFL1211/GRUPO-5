from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from .categorias import OUTRAS, categoria_da_habilidade
from .models import Favorito, Habilidade, Usuario


class CategoriaDaHabilidadeTests(SimpleTestCase):
    def test_reconhece_ignorando_acento_e_maiuscula(self):
        self.assertEqual(categoria_da_habilidade('INGLES'), 'Idiomas')
        self.assertEqual(categoria_da_habilidade('violão'), 'Música')
        self.assertEqual(categoria_da_habilidade('Excel'), 'Tecnologia e Programação')

    def test_reconhece_quando_o_nome_tem_mais_palavras(self):
        self.assertEqual(categoria_da_habilidade('Inglês (conversação)'), 'Idiomas')
        self.assertEqual(categoria_da_habilidade('Python para iniciantes'), 'Tecnologia e Programação')
        self.assertEqual(categoria_da_habilidade('Teoria musical'), 'Música')

    def test_termo_precisa_comecar_uma_palavra(self):
        self.assertEqual(categoria_da_habilidade('Recanto'), OUTRAS)   # não é "canto"

    def test_desconhecida_vira_outras(self):
        self.assertEqual(categoria_da_habilidade('Origami'), OUTRAS)
        self.assertEqual(categoria_da_habilidade(''), OUTRAS)


class BuscaEFiltroTests(TestCase):
    def setUp(self):
        def criar(nome, login, habilidades):
            user = User.objects.create_user(login, password='teste')
            usuario = Usuario.objects.create(user=user, nome=nome)
            for h in habilidades:
                Habilidade.objects.create(usuario=usuario, nome=h, tipo='ensinar')
            return usuario
        self.ana = criar('Ana Souza', 'ana@teste.com', ['Inglês'])
        self.bruno = criar('Bruno Lima', 'bruno@teste.com', ['Violão', 'Fotografia'])
        self.carla = criar('Carla Dias', 'carla@teste.com', ['Excel', 'Origami'])
        self.client.force_login(self.ana.user)
        self.url = reverse('lista_habilidades')

    def nomes(self, **params):
        pagina = self.client.get(self.url, params)
        return [h.nome for h in pagina.context['habilidades']]

    def test_sem_filtro_mostra_todas_menos_as_proprias(self):
        self.assertEqual(sorted(self.nomes()), ['Excel', 'Fotografia', 'Origami', 'Violão'])

    def test_busca_por_habilidade_ignora_acento_e_maiuscula(self):
        self.assertEqual(self.nomes(q='VIOLAO'), ['Violão'])
        self.assertEqual(self.nomes(q='  fotogr '), ['Fotografia'])

    def test_busca_por_nome_da_pessoa(self):
        self.assertEqual(sorted(self.nomes(q='carla')), ['Excel', 'Origami'])

    def test_filtro_por_categoria(self):
        self.assertEqual(self.nomes(categoria='Música'), ['Violão'])
        self.assertEqual(self.nomes(categoria='Outras'), ['Origami'])
        self.assertEqual(self.nomes(categoria='Idiomas'), [])   # a única de Idiomas é da própria Ana

    def test_busca_e_categoria_juntas(self):
        self.assertEqual(self.nomes(q='bruno', categoria='Artes e Criatividade'), ['Fotografia'])
        self.assertEqual(self.nomes(q='bruno', categoria='Música'), ['Violão'])
        self.assertEqual(self.nomes(q='carla', categoria='Música'), [])

    def test_categoria_invalida_e_ignorada(self):
        self.assertEqual(len(self.nomes(categoria='<script>')), 4)

    def test_sem_resultado_mostra_aviso_e_botao_limpar(self):
        pagina = self.client.get(self.url, {'q': 'xyz'})
        self.assertContains(pagina, 'Nenhuma habilidade encontrada')
        self.assertContains(pagina, 'Limpar')

    def test_campos_voltam_preenchidos_e_texto_e_escapado(self):
        pagina = self.client.get(self.url, {'q': '<b>x</b>', 'categoria': 'Música'})
        self.assertContains(pagina, '&lt;b&gt;x&lt;/b&gt;')
        self.assertNotContains(pagina, '<b>x</b>')
        self.assertContains(pagina, 'value="Música" selected')

    def test_card_mostra_a_categoria(self):
        self.assertContains(self.client.get(self.url, {'q': 'violao'}), 'fav-categoria">Música')

    def test_favoritar_volta_para_a_busca_com_os_filtros(self):
        violao = Habilidade.objects.get(nome='Violão')
        pagina = self.client.get(self.url, {'q': 'violao', 'categoria': 'Música'})
        self.assertContains(pagina, 'value="/habilidades/?q=violao&amp;categoria=M%C3%BAsica"')
        resposta = self.client.post(reverse('alternar_favorito', args=[violao.pk]),
                                    {'next': '/habilidades/?q=violao&categoria=M%C3%BAsica'})
        self.assertRedirects(resposta, '/habilidades/?q=violao&categoria=M%C3%BAsica')
        self.assertTrue(Favorito.objects.filter(usuario=self.ana, habilidade=violao).exists())

    def test_tela_de_favoritas_tambem_mostra_a_categoria(self):
        violao = Habilidade.objects.get(nome='Violão')
        Favorito.objects.create(usuario=self.ana, habilidade=violao)
        self.assertContains(self.client.get(reverse('habilidades_favoritas')), 'fav-categoria">Música')
