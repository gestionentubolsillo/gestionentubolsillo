from django.contrib.messages import get_messages
from home.tests import BaseTests
from .models import Servicio

# Create your tests here.

class ServicioTest(BaseTests):
    def setUp(self):
        super().setUp()
        servicio_auth = Servicio(cuenta=self.logged_user.cuenta,
            nombre='prueba__',empresa=self.logged_user.empresa)
        servicio_auth.save()

        self.servicio_auth = servicio_auth

        servicio_not_auth = Servicio(cuenta=self.other_user.cuenta,
            nombre='notauth__',empresa=self.other_user.empresa)
        servicio_not_auth.save()
        
        self.servicio_not_auth = servicio_not_auth

class ServicioTestsView(ServicioTest):
    
    def test_list_possitive(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/servicios',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['servicios'].paginator.count,1)

    def test_view_servicio_possitive(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/servicios/{self.servicio_auth.ServicioID}',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['servicio'].ServicioID,self.servicio_auth.ServicioID)

    def test_view_servicio_unauth_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/servicios/{self.servicio_not_auth.ServicioID}')
        self.assertEqual(response.status_code,302)

    def test_view_servicio_non_existent_fails(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/servicios/999',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/servicios')
        self.assertEqual(response.status_code,200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')
        self.assertEqual(str(messages[0]),"El servicio no existe")


class ServicioTestsCreate(ServicioTest):
    pass

class ServicioTestsDelete(ServicioTest):
    pass

class ServicioTestsEdit(ServicioTest):
    pass
