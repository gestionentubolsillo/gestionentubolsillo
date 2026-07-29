from django.contrib.messages import get_messages
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

class DelegacionTestsCreate(DelegacionTest):

    def test_delegacion_create_possitive(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/delegaciones/create', data={
            'nombre':'create__'
        },format='json',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/delegaciones')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['delegaciones'].paginator.count,2)

class DelegacionTestsDelete(DelegacionTest):

    def test_delegacion_delete_possitive(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/delegaciones/delete/{self.delegacion_auth.DelegacionID}',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/delegaciones')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['delegaciones'].paginator.count,0)

    def test_delegacion_delete_unauth_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/delegaciones/delete/{self.delegacion_no_auth.DelegacionID}',follow=True)
        self.assertEqual(response.status_code,404)

    def test_delegacion_delete_non_existent_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/delegaciones/delete/999',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/delegaciones')
        self.assertEqual(response.context['delegaciones'].paginator.count,1)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')
        self.assertEqual(str(messages[0]),"La delegación no existe")
