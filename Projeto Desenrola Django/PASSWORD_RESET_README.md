# Recuperação de senha

Execute na pasta que contém manage.py:

    python manage.py test Desenrola.test_password_reset
    python manage.py runserver

Sem EMAIL_HOST, o link aparece no terminal (apenas desenvolvimento).

Para envio real, configure as variáveis de ambiente ou Codespaces Secrets:

- EMAIL_HOST: servidor SMTP (por exemplo smtp.gmail.com)
- EMAIL_PORT: 587 (TLS)
- EMAIL_HOST_USER: endereço da conta de envio
- EMAIL_HOST_PASSWORD: senha de aplicativo do provedor, nunca a senha em código
- DEFAULT_FROM_EMAIL: remetente autorizado (opcional)
- DJANGO_SECRET_KEY: chave aleatória privada, estável e compartilhada entre instâncias
- PASSWORD_RESET_DOMAIN: domínio público confiável do site, sem https:// nem barra final; no Codespaces use o hostname da porta 8000.

Reinicie o servidor após configurar. Use um endereço cadastrado e acessível para testar a entrega. O link é válido por uma hora e usa HTTPS quando o domínio é configurado. Antes de disponibilizar publicamente, restrinja ALLOWED_HOSTS, desative DEBUG, configure o proxy confiável e limite a frequência de solicitações de recuperação. O modo console não deve ser utilizado em produção.
