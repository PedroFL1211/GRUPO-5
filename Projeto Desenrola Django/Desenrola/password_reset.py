from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.utils.translation import override

class DesenrolaPasswordResetForm(PasswordResetForm):
    def save(self, *args, **kwargs):
        if settings.PASSWORD_RESET_DOMAIN:
            kwargs["domain_override"] = settings.PASSWORD_RESET_DOMAIN
            kwargs["use_https"] = True
        with override("pt-br"):
            return super().save(*args, **kwargs)

class DesenrolaPasswordResetView(PasswordResetView):
    form_class = DesenrolaPasswordResetForm
