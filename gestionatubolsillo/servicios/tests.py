from django.http import HttpResponse
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

    def _assertErrorOnCreate(self,response:HttpResponse):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='servicios/form.html')
        self.assertFalse(Servicio.objects.filter(nombre='error__').exists())

    def test_create_servicio_possitive(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/servicios/create',data={
            'nombre':'new__','empresa_id':self.logged_user.empresa.EmpresaID
        },format='json',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/servicios')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['servicios'].paginator.count,2)

    def test_create_servicio_possitive_with_dias_and_horas(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/servicios/create',data={
            'nombre':'new__','empresa_id':self.logged_user.empresa.EmpresaID,
            'dias_semana':['lunes','domingo'],'hora_inicio':'08:00','hora_fin':'14:00'
        },format='json',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/servicios')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['servicios'].paginator.count,2)

    def test_create_servicio_empresa_not_auth_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/servicios/create',data={
            'nombre':'error__','empresa_id':self.other_user.empresa.EmpresaID
        },format='json',follow=True)
        self._assertErrorOnCreate(response)

    def test_create_servicio_empresa_not_exists_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/servicios/create',data={
            'nombre':'error__','empresa_id':999
        },format='json',follow=True)
        self._assertErrorOnCreate(response)

    def test_create_servicio_empresa_invalid_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/servicios/create',data={
            'nombre':'error__','empresa_id':''
        },format='json',follow=True)
        self._assertErrorOnCreate(response)

    def test_create_servicio_horas_invalid_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/servicios/create',data={
            'nombre':'error__','empresa_id':self.logged_user.empresa.EmpresaID,
            'dias_semana':['lunes','domingo'],'hora_inicio':'XXXX','hora_fin':'XXXX'
        },format='json',follow=True)
        self._assertErrorOnCreate(response)

    def test_create_servicio_dias_invalid_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/servicios/create',data={
            'nombre':'error__','empresa_id':self.logged_user.empresa.EmpresaID,
            'dias_semana':['luneX','domiXgo'],'hora_inicio':'08:00','hora_fin':'14:00'
        },format='json',follow=True)
        self._assertErrorOnCreate(response)


class ServicioTestsDelete(ServicioTest):

    def test_delete_servicio_possitive(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/servicios/delete/{self.servicio_auth.ServicioID}',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/servicios')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['servicios'].paginator.count,0)

    def test_delete_servicio_unauth_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/servicios/delete/{self.servicio_not_auth.ServicioID}',follow=True)
        self.assertEqual(response.status_code,404)
    
    def test_delete_servicio_non_existent_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/servicios/delete/999',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/servicios')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['servicios'].paginator.count,1)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')
        self.assertEqual(str(messages[0]),"El servicio no existe")

class ServicioTestsEdit(ServicioTest):
    pass
