import re
from urllib.parse import urlsplit
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

@override_settings(PASSWORD_RESET_DOMAIN="example.test", MAILERS={"default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"}})
class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="teste@example.test", email="teste@example.test", password="SenhaAntiga!123")

    def test_reset_flow(self):
        response = self.client.post(reverse("password_reset"), {"email": self.user.email})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        link = re.search(r"https://example\.test/\S+", mail.outbox[0].body).group()
        path = urlsplit(link).path
        response = self.client.get(path)
        self.assertEqual(response.status_code, 302)
        new_path = response.url
        response = self.client.post(new_path, {"new_password1": "NovaSenha!7392", "new_password2": "NovaSenha!7392"})
        self.assertRedirects(response, reverse("password_reset_complete"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NovaSenha!7392"))
        self.assertContains(self.client.get(path), "inválido")

    def test_unknown_email(self):
        response = self.client.post(reverse("password_reset"), {"email": "unknown@example.test"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)

    def test_login_link(self):
        self.assertContains(self.client.get(reverse("login")), reverse("password_reset"))
