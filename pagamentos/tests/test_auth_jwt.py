from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class JWTAuthTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="usuario_teste", password="senha-super-secreta"
        )

    def test_obter_token_e_acessar_rota_protegida(self):
        token_url = reverse("token_obtain_pair")
        auth_ping_url = reverse("auth-ping")

        # sem token deve falhar
        resposta_sem_token = self.client.get(auth_ping_url)
        self.assertEqual(resposta_sem_token.status_code, status.HTTP_401_UNAUTHORIZED)

        # obter token JWT
        resposta_token = self.client.post(
            token_url,
            {"username": "usuario_teste", "password": "senha-super-secreta"},
            format="json",
        )
        self.assertEqual(resposta_token.status_code, status.HTTP_200_OK)
        self.assertIn("access", resposta_token.data)
        self.assertIn("refresh", resposta_token.data)

        token_de_acesso = resposta_token.data["access"]

        # usar token na rota protegida
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_de_acesso}")
        resposta_com_token = self.client.get(auth_ping_url)
        self.assertEqual(resposta_com_token.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta_com_token.data["ok"], True)
        self.assertEqual(resposta_com_token.data["user"], self.user.username)

