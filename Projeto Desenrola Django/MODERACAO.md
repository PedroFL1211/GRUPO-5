# Painel de moderação de denúncias

Implementado no Django existente em `Projeto Desenrola Django`, reutilizando `Denuncia`, `Usuario`, os logins do Django e o CSS da página de denúncias.

## Ativar

Na pasta `Projeto Desenrola Django`:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Entre em `/accounts/login/` com uma conta de equipe (`is_staff=True`) ou superusuário. O link **Moderação** aparece na home para essas contas; endereço: `/moderacao/denuncias/`.

## Uso

- A página `/denunciar/` permite selecionar um usuário real ou uma das habilidades que ele ensina. A seleção vincula a denúncia ao perfil correto.
- O painel lista as denúncias da mais recente para a mais antiga, com filtro e paginação de 20 registros.
- Status disponíveis: aberta, em análise e resolvida. É possível reabrir uma denúncia pelo seletor de status.
- A remoção exige confirmação e resolve a denúncia. Todas as mudanças ficam no histórico com moderador e data.
- Remover usuário exclui seu `Usuario` e seu login do Django, ligados pelo mesmo username no cadastro atual. Relações com exclusão em cascata seguem os models existentes.
- Remover habilidade retira apenas a habilidade denunciada do campo `habilidadeEnsina` do dono. As recomendações já usam esse campo e refletem a mudança.
- Não existe model Habilidade no projeto atual. O painel usa as habilidades separadas por vírgula, ponto e vírgula ou barra, seguindo a lógica existente em `recomendacoes.py`.
- Denúncias antigas, cujo alvo era texto livre, continuam listadas e podem mudar de status. Não é feita associação automática por nome: sua remoção fica indisponível para evitar excluir um alvo incorreto.
- O alvo em texto e a denúncia são preservados após a remoção do perfil. O painel não permite excluir contas de equipe nem o próprio moderador.
- Os perfis públicos `marina` e `thiago` continuam sendo exemplos fixos no projeto original; não são registros removíveis do banco.

## Verificação

```bash
python manage.py test Desenrola
python manage.py makemigrations --check --dry-run
python manage.py check
```

Os testes cobrem restrição por equipe, CSRF, escape de relatos, status e histórico, seleção de alvo, remoção de login/perfil, preservação de denúncias e remoção de habilidade com efeito nas recomendações.
