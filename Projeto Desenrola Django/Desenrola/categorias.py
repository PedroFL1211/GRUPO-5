"""
Categorias das habilidades do Desenrola.

A lista vem do documento "Definição de Categorias de Habilidades" (pasta Pesquisa).
Não mexe no banco: a categoria é descoberta a partir do NOME da habilidade.
Como o nome é texto livre, o que não estiver na lista cai em "Outras".
Para reconhecer mais habilidades, é só acrescentar o nome na lista da categoria.
"""
import re

from .recomendacoes import normalizar

OUTRAS = "Outras"

CATEGORIAS = {
    "Idiomas": ["Inglês", "Espanhol", "Francês", "Libras", "Italiano"],
    "Tecnologia e Programação": ["Python", "JavaScript", "HTML e CSS", "Desenvolvimento de sites", "Excel", "Programação"],
    "Artes e Criatividade": ["Desenho", "Pintura", "Fotografia", "Edição de vídeos", "Design gráfico", "Design"],
    "Música": ["Violão", "Piano", "Canto", "Guitarra", "Teoria musical", "Música"],
    "Educação e Estudos": ["Matemática", "Física", "Química", "Redação", "Técnicas de estudo"],
    "Negócios e Finanças": ["Educação financeira", "Empreendedorismo", "Marketing digital", "Gestão de projetos",
                            "Organização financeira", "Finanças"],
    "Saúde e Bem-estar": ["Yoga", "Meditação", "Alongamento", "Hábitos saudáveis", "Técnicas de relaxamento"],
    "Esportes e Atividades Físicas": ["Futebol", "Vôlei", "Dança", "Corrida", "Xadrez", "Esporte"],
    "Culinária": ["Receitas básicas", "Confeitaria", "Panificação", "Culinária vegetariana", "Técnicas de cozinha",
                  "Culinária", "Cozinha"],
    "Desenvolvimento Pessoal e Profissional": ["Comunicação", "Oratória", "Organização pessoal",
                                               "Preparação para entrevistas", "Elaboração de currículos"],
}

# Nomes que aparecem no filtro (as 10 categorias + "Outras")
NOMES_DAS_CATEGORIAS = list(CATEGORIAS) + [OUTRAS]

# Termos já normalizados, dos mais longos para os mais curtos ("teoria musical" antes de "musica")
_TERMOS = sorted(
    ((normalizar(termo), categoria) for categoria, termos in CATEGORIAS.items() for termo in termos),
    key=lambda par: len(par[0]),
    reverse=True,
)


def categoria_da_habilidade(nome):
    """'Inglês (conversação)' -> 'Idiomas'   |   'Origami' -> 'Outras'

    O termo precisa começar uma palavra: 'canto' reconhece 'Canto lírico',
    mas não reconhece 'Recanto'."""
    texto = normalizar(nome)
    for termo, categoria in _TERMOS:
        if re.search(r"(?<![a-z0-9])" + re.escape(termo), texto):
            return categoria
    return OUTRAS
