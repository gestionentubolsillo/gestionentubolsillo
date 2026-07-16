from home.tests import BaseTests
from .models import Delegacion

# Create your tests here.

class DelegacionTest(BaseTests):

    def setUp(self):
        super().setUp()
        delegacion_auth = Delegacion(nombre='prueba__',
            cuenta=self.logged_user.cuenta,usuario_creador=self.logged_user)
        delegacion_auth.save()

        self.delegacion_auth = delegacion_auth

        delegacion_no_auth = Delegacion(nombre='noauth__',
            cuenta=self.other_user.cuenta,usuario_creador=self.other_user)
        delegacion_no_auth.save()

        self.delegacion_no_auth = delegacion_no_auth

class DelegacionTestsView(DelegacionTest):

    def test_delegacion_list_possitive(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/delegaciones')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['delegaciones'].paginator.count,1)

    def test_delegacion_view_possitive(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/delegaciones/{self.delegacion_auth.DelegacionID}')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['delegacion'].DelegacionID,self.delegacion_auth.DelegacionID)

    def test_delegacion_view_unauth_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/delegaciones/{self.delegacion_no_auth.DelegacionID}')
        self.assertEqual(response.status_code,302)