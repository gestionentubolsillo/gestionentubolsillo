from django.http import HttpResponse
from django.contrib.messages import get_messages

from users.models import User, PermisosModulo, Cuenta
from empresas.models import Empresa
from home.tests import BaseTests


class CuadranteTests(BaseTests):

    def setUp(self):
        super().setUp()

    def test_logged_user_list_own_cuadrantes(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/users/{self.logged_user.UserID}/cuadrantes')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['cuadrantes'].paginator.count,0)

    def test_logged_user_tries_list_other_cuadrantes_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/users/{self.other_user.UserID}/cuadrantes')
        #self.assertRedirects(response,expected_url='/AuthError')
        self.assertEqual(response.status_code,302)