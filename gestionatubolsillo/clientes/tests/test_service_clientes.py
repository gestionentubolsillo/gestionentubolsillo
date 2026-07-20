from django.contrib.messages import get_messages
from .base import ClienteTest
from servicios.models import Servicio

class ClienteServiceTest(ClienteTest):

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

class ClienteServiceTestsAdd(ClienteServiceTest):

    def test_add_servicio_possitive(self):
        self.assertLogin()
        #Check there is no services assigned before
        response = self.client.get(path=f'/backoffice/clientes/{self.cliente_auth.ClienteID}')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['servicios'].paginator.count,0)
        response = self.client.post(path=f'/backoffice/clientes/{self.cliente_auth.ClienteID}/servicios/add',data={
            'servicios_ids':[self.servicio_auth.ServicioID]
        },format='json',follow=True)
        #Check there is 1 service assigned after post
        self.assertRedirects(response,expected_url=f'/backoffice/clientes/{self.cliente_auth.ClienteID}')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['servicios'].paginator.count,1)

    def test_add_servicio_unauth_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/clientes/{self.cliente_auth.ClienteID}/servicios/add',data={
            'servicios_ids':[self.servicio_not_auth.ServicioID]
        },format='json',follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='clientes/add_servicio.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')

    def test_add_servicio_to_unauth_client_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/clientes/{self.cliente_not_auth.ClienteID}/servicios/add',data={
            'servicios_ids':[self.servicio_not_auth.ServicioID]
        },format='json',follow=True)
        self.assertEqual(response.status_code,404)
        self.cliente_not_auth.refresh_from_db()
        self.assertFalse(self.cliente_not_auth.servicios.count()>0)

    def test_add_servicio_invalid_format_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/clientes/{self.cliente_auth.ClienteID}/servicios/add',data={
            'servicios_ids':['']
        },format='json',follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='clientes/add_servicio.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')

class ClienteServiceTestsRemove(ClienteServiceTest):

    def setUp(self):
        super().setUp()
        self.cliente_auth.servicios.set(Servicio.objects.filter(ServicioID=self.servicio_auth.ServicioID))
        self.cliente_not_auth.servicios.set(Servicio.objects.filter(ServicioID=self.servicio_not_auth.ServicioID))

        servicio_not_assigned = Servicio(cuenta=self.logged_user.cuenta,
            nombre='NA__',empresa=self.logged_user.empresa)
        servicio_not_assigned.save()
        self.servicio_not_assigned = servicio_not_assigned

    def test_remove_service_possitive(self):
        self.assertLogin()
        #Check there is 1 service assigned before
        response = self.client.get(path=f'/backoffice/clientes/{self.cliente_auth.ClienteID}')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['servicios'].paginator.count,1)
        response = self.client.post(path=f'/backoffice/clientes/{self.cliente_auth.ClienteID}/servicios/remove',data={
            'servicios_ids':[self.servicio_auth.ServicioID]
        },format='json',follow=True)
        #Check there is no services assigned after post
        self.assertRedirects(response,expected_url=f'/backoffice/clientes/{self.cliente_auth.ClienteID}')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['servicios'].paginator.count,0)

    def test_remove_unassigned_service_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/clientes/{self.cliente_auth.ClienteID}/servicios/remove',data={
            'servicios_ids':[self.servicio_not_assigned.ServicioID]
        },format='json',follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='clientes/add_servicio.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')