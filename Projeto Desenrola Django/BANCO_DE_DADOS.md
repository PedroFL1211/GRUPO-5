# Banco de dados — Desenrola

O projeto usa Django com SQLite por padrão. As tabelas são criadas pelas migrações do Django; não é necessário criar as tabelas manualmente no SQLite.

## Tabelas

- `usuarios_usuario`: perfil, nome de usuário e habilidades que a pessoa ensina/aprende.
- `usuarios_habilidade`: anúncio de habilidade, com mentor, descrição, categoria, nível, formato, preço e disponibilidade.
- `usuarios_sessao`: solicitação/agendamento de uma aula, ligada ao anúncio e ao aprendiz.
- `usuarios_avaliacao`: nota e comentário após uma sessão; cada avaliador pode avaliar uma sessão uma vez e a nota deve estar entre 1 e 5.
- `usuarios_favorito`: relação entre usuário e anúncio favorito, sem duplicatas.
- `usuarios_denuncia`: denúncia de um usuário e/ou anúncio, com motivo e status.

As chaves primárias são criadas automaticamente pelo Django. Os campos `ForeignKey` viram chaves estrangeiras. Ao remover um registro referenciado, o comportamento definido nos modelos é `CASCADE`.

## Aplicar no projeto

No terminal, entre na pasta `Projeto Desenrola Django`, ative seu ambiente virtual e execute:

```bash
python manage.py makemigrations usuarios
python manage.py migrate
python manage.py showmigrations usuarios
```

A primeira linha gera uma migração a partir dos modelos; a segunda aplica as migrações e cria/atualiza as tabelas no arquivo `db.sqlite3`; a terceira permite conferir quais migrações foram aplicadas.

Se a migração `0002_funcionalidades` já estiver no repositório, `makemigrations` pode informar que não há mudanças pendentes. Nesse caso, basta executar `python manage.py migrate`.

Para conferir o SQL que o Django gerou:

```bash
python manage.py sqlmigrate usuarios 0002
```

## Escopo

As tabelas cobrem o núcleo dos requisitos documentados: perfil, publicação/busca de habilidades, agendamento, avaliação, favoritos e denúncias. Pagamentos, chat, notificações, certificados e grupos ainda exigem modelagem própria antes de serem implementados.
