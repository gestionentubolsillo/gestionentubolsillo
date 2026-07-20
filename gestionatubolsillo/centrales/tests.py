from django.contrib.messages import get_messages
from home.tests import BaseTests
from .models import Central

# Create your tests here.
class CentralTest(BaseTests):
    
    def setUp(self):
        super().setUp()

        central_auth = Central(nombre='prueba__',
            usuario_creador=self.logged_user,cuenta=self.logged_user.cuenta)
        central_auth.save()
        self.central_auth = central_auth

        central_no_auth = Central(nombre='notauth__',
            usuario_creador=self.other_user,cuenta=self.other_user.cuenta)
        central_no_auth.save()
        self.central_no_auth = central_no_auth

class CentralTestsView(CentralTest):

    def test_list_centrales(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/centrales',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['centrales'].paginator.count,1)

    def test_view_central_possitive(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/centrales/{self.central_auth.CentralID}',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['central'].CentralID,self.central_auth.CentralID)

    def test_view_central_unauth_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/centrales/{self.central_no_auth.CentralID}')
        self.assertEqual(response.status_code,302)


class CentralTestsCreate(CentralTest):

    def test_create_central_possitive(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/centrales/create',data={
            'nombre':'create__'
        },format='json',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/centrales')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['centrales'].paginator.count,2)

class CentralTestsDelete(CentralTest):

    def test_delete_central_possitive(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/centrales/delete/{self.central_auth.CentralID}',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/centrales')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['centrales'].paginator.count,0)

    def test_delete_central_unauth_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/centrales/delete/{self.central_no_auth.CentralID}',follow=True)
        self.assertEqual(response.status_code,404)

    def test_delete_central_non_existent_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/centrales/delete/999',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/centrales')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['centrales'].paginator.count,1)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')
        self.assertEqual(str(messages[0]),"La central receptora no existe")
