from django.http import HttpResponse
from home.tests import BaseTests
from .models import Sugerencia

# Create your tests here.
class SugerenciaTest(BaseTests):

    def setUp(self):
        super().setUp()

        sugerencia_auth = Sugerencia(cuenta=self.logged_user.cuenta,
            texto='prueba__',usuario_creador=self.logged_user,usuario_referente=self.logged_user,
            empresa=self.logged_user.empresa)
        sugerencia_auth.save()

        self.sugerencia_auth = sugerencia_auth

        sugerencia_other = Sugerencia(cuenta=self.other_user.cuenta,
            texto='prueba__',usuario_creador=self.other_user,usuario_referente=self.other_user,
            empresa=self.other_user.empresa)
        sugerencia_other.save()

        self.sugerencia_other = sugerencia_other

class SugerenciaTestsView(SugerenciaTest):

    def test_list_sugerencias_possitive(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/sugerencias')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['sugerencias'].paginator.count,1)
        encontrada_sug_auth = any(sugerencia.SugerenciaID == self.sugerencia_auth.SugerenciaID
            for sugerencia in response.context['sugerencias'])
        self.assertTrue(encontrada_sug_auth)
        encontrada_sug_not_auth = any(sugerencia.SugerenciaID == self.sugerencia_other.SugerenciaID
            for sugerencia in response.context['sugerencias'])
        self.assertFalse(encontrada_sug_not_auth)

    def test_list_sugerencias_self_positive(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/sugerencias/self')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['sugerencias'].paginator.count,1)
        encontrada_sug_auth = any(sugerencia.SugerenciaID == self.sugerencia_auth.SugerenciaID
            for sugerencia in response.context['sugerencias'])
        self.assertTrue(encontrada_sug_auth)
        encontrada_sug_not_auth = any(sugerencia.SugerenciaID == self.sugerencia_other.SugerenciaID
            for sugerencia in response.context['sugerencias'])
        self.assertFalse(encontrada_sug_not_auth)


class SugerenciaTestsCreate(SugerenciaTest):

    def _assertCreateError(self,response:HttpResponse):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='sugerencias/form.html')
        self.assertFalse(Sugerencia.objects.filter(texto='error__').exists())


    def test_create_possitive(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/sugerencias/create',data={
            'texto':'create__','departamento':'','user_ref_id':self.logged_user.UserID
        },format='json',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/sugerencias')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['sugerencias'].paginator.count,2)

    def test_create_user_auth_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/sugerencias/create',data={
            'texto':'error__','departamento':'','user_ref_id':self.other_user.UserID
        },format='json',follow=True)
        self._assertCreateError(response)

    def test_create_user_not_exists_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/sugerencias/create',data={
            'texto':'error__','departamento':'','user_ref_id':999
        },format='json',follow=True)
        self._assertCreateError(response)
        
    
    def test_create_user_invalid_arg_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/sugerencias/create',data={
            'texto':'error__','departamento':'','user_ref_id':''
        },format='json',follow=True)
        self._assertCreateError(response)
    

class SugerenciaTestsDelete(SugerenciaTest):
    
    def test_delete_possitive(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/sugerencias/{self.sugerencia_auth.SugerenciaID}/delete',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/sugerencias')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['sugerencias'].paginator.count,0)

    def test_delete_unauth_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/sugerencias/{self.sugerencia_other.SugerenciaID}/delete',follow=True)
        self.assertEqual(response.status_code,404)
        self.assertFalse(Sugerencia.objects.filter(SugerenciaID=self.sugerencia_other.SugerenciaID,estado='borrada').exists())


class SugerenciaTestsEdit(SugerenciaTest):
    pass
