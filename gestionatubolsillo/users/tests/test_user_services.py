from django.http import HttpResponse
from django.contrib.messages import get_messages

from users.models import User
from servicios.models import Servicio

from home.tests import BaseTests

class ServiceTests(BaseTests):

    def setUp(self):
        super().setUp()
        servicio_to_add = Servicio(cuenta=self.logged_user.cuenta,
            nombre='toadd__',empresa=self.logged_user.empresa)
        servicio_to_add.save()
        servicio_to_remove = Servicio(cuenta=self.logged_user.cuenta,
            nombre='toremove__',empresa=self.logged_user.empresa)
        servicio_to_remove.save()
        other_servicio = Servicio(cuenta=self.other_user.cuenta,
            nombre='otherservice__',empresa=self.other_user.empresa)
        other_servicio.save()

        self.servicio_to_add = servicio_to_add
        self.servicio_to_remove = servicio_to_remove
        self.other_servicio = other_servicio

        user_services = Servicio.objects.filter(nombre='toremove__')
        self.logged_user.servicios.set(user_services)

    def _assertValidationErrorOnAdd(self,response):
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='account/users/services/form.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')
        self.assertEqual(str(messages[0]),"Los servicios deben ser válidos")

    def _assertListViewDidNotChange(self,response):
        self.assertRedirects(response,expected_url=f'/backoffice/users/{self.logged_user.UserID}/services')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,template_name='account/users/services/list.html')
        self.assertEqual(response.context['servicios'].paginator.count,1)

    def test_list_servicios_of_user_possitive(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/users/{self.logged_user.UserID}/services', follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='account/users/services/list.html')
        self.assertEqual(response.context['servicios'].paginator.count,1)
    
    def test_list_servicios_of_unauth_user_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/users/{self.other_user.UserID}/services')
        self.assertEqual(response.status_code,302)

    def test_add_servicio_to_user_possitive(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/{self.logged_user.UserID}/services/assign',data={
            'servicios_ids':[self.servicio_to_add.ServicioID]
        },format='json',follow=True)
        self.assertRedirects(response,expected_url=f'/backoffice/users/{self.logged_user.UserID}/services')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,template_name='account/users/services/list.html')
        self.assertEqual(response.context['servicios'].paginator.count,2)

    def test_add_servicio_other_cuenta_to_user_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/{self.logged_user.UserID}/services/assign',data={
            'servicios_ids':[self.other_servicio.ServicioID]
        },format='json',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='account/users/services/form.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(str(messages[0]),"Los servicios deben pertenecer a la misma empresa que el usuario para ser asignados")
        self.assertEqual(messages[0].extra_tags,'error')

    def test_add_non_existent_servicio_to_user_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/{self.logged_user.UserID}/services/assign',data={
            'servicios_ids':[999]
        },format='json',follow=True)
        self._assertValidationErrorOnAdd(response)

    def test_add_invalid_servicio_to_user_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/{self.logged_user.UserID}/services/assign',data={
            'servicios_ids':['']
        },format='json',follow=True)
        self._assertValidationErrorOnAdd(response)
        

    def test_remove_servicio_to_user_possitive(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/{self.logged_user.UserID}/services/remove',data={
            'servicios_ids':[self.servicio_to_remove.ServicioID]
        },format='json',follow=True)
        self.assertRedirects(response,expected_url=f'/backoffice/users/{self.logged_user.UserID}/services')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,template_name='account/users/services/list.html')
        self.assertEqual(response.context['servicios'].paginator.count,0)

    def test_remove_unnasigned_service_to_user_does_nothing(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/{self.logged_user.UserID}/services/remove',data={
            'servicios_ids':[self.servicio_to_add.ServicioID]
        },format='json',follow=True)
        self._assertListViewDidNotChange(response)

    def test_remove_non_existent_service_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/{self.logged_user.UserID}/services/remove',data={
            'servicios_ids':[999]
        },format='json',follow=True)
        self._assertListViewDidNotChange(response)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')
        self.assertEqual(str(messages[0]),"Los servicios deben ser válidos")

    def test_remove_invalid_service_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/{self.logged_user.UserID}/services/remove',data={
            'servicios_ids':['']
        },format='json',follow=True)
        self._assertListViewDidNotChange(response)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')
        self.assertEqual(str(messages[0]),"Los servicios deben ser válidos")

    