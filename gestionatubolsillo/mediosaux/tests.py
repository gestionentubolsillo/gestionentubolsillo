from django.contrib.messages import get_messages
from home.tests import BaseTests
from .models import MedioAuxiliar

# Create your tests here.

class MedioAuxTest(BaseTests):
    def setUp(self):
        super().setUp()
        medio_auth = MedioAuxiliar(cuenta=self.logged_user.cuenta,
            nombre='medio__',usuario_creador=self.logged_user)
        medio_auth.save()

        self.medio_auth = medio_auth

        medio_not_auth = MedioAuxiliar(cuenta=self.other_user.cuenta,
            nombre='notauth__',usuario_creador=self.other_user)
        medio_not_auth.save()

        self.medio_not_auth = medio_not_auth

class MedioAuxTestsView(MedioAuxTest):

    def test_list_possitive(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/medios_auxiliares',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['medios_auxiliares'].paginator.count,1)

    def test_medio_view_possitive(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/medios_auxiliares/{self.medio_auth.MedioAuxiliarID}',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['medio_auxiliar'].MedioAuxiliarID,self.medio_auth.MedioAuxiliarID)

    def test_medio_view_unauth_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/medios_auxiliares/{self.medio_not_auth.MedioAuxiliarID}')
        self.assertEqual(response.status_code,302)

    def test_medio_view_non_existent_fails(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/medios_auxiliares/999',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/medios_auxiliares')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')
        self.assertEqual(str(messages[0]),"El medio auxiliar no existe")

class MedioAuxTestsCreate(MedioAuxTest):

    def test_create_medio_possitive(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/medios_auxiliares/create',data={
            'nombre':'prueba__'
        },format='json',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/medios_auxiliares')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['medios_auxiliares'].paginator.count,2)

    def test_create_medio_nombre_missing_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/medios_auxiliares/create',data={
            'nombre':''
        },format='json',follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='mediosaux/form.html')
        self.assertFalse(MedioAuxiliar.objects.all().count()>2)

class MedioAuxTestsDelete(MedioAuxTest):

    def test_delete_medio_possitive(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/medios_auxiliares/delete/{self.medio_auth.MedioAuxiliarID}',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/medios_auxiliares')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['medios_auxiliares'].paginator.count,0)

    def test_delete_medio_unauth_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/medios_auxiliares/delete/{self.medio_not_auth.MedioAuxiliarID}',follow=True)
        self.assertEqual(response.status_code,404)

    def test_delete_medio_non_existent_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/medios_auxiliares/delete/999',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/medios_auxiliares')
        self.assertEqual(response.status_code,200)
        self.assertFalse(MedioAuxiliar.objects.all().count()<2)

