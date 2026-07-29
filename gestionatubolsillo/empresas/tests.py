from home.tests import BaseTests
from .models import Empresa

# Create your tests here.

class EmpresaTest(BaseTests):

    def setUp(self):
        super().setUp()

class EmpresaTestsView(EmpresaTest):

    def test_list_empresa_possitive(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/empresas',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['empresa_usuario'].EmpresaID,self.logged_user.empresa.EmpresaID)
        self.assertEqual(response.context['empresas'].paginator.count+1,1)
    
    def test_view_empresa_possitive(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/empresas/{self.logged_user.empresa.EmpresaID}',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['empresa'].EmpresaID,self.logged_user.empresa.EmpresaID)

    def test_view_empresa_unauth_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/empresas/{self.other_user.empresa.EmpresaID}')
        self.assertEqual(response.status_code,302)

class EmpresaTestsCreate(EmpresaTest):

    def test_create_empresa_possitive(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/empresas/create',data={
            'name':'create__','paquete':'seguridad'
        },format='json',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/empresas')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['empresas'].paginator.count+1,2)

    def test_create_empresa_paquete_not_valid_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/empresas/create',data={
            'name':'error__','paquete':'XXXXXX'
        },format='json',follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='empresas/form.html')
        self.assertFalse(Empresa.objects.filter(nombre='error__').exists())

class EmpresaTestsDelete(EmpresaTest):

    def setUp(self):
        super().setUp()
        empresa_to_delete = Empresa(nombre='todelete__',paquete='auxiliares',
            cuenta=self.logged_user.cuenta,usuario_creador=self.logged_user)
        empresa_to_delete.save()

        self.empresa_to_delete = empresa_to_delete

    def test_delete_empresa_possitive(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/empresas')
        self.assertEqual(response.context['empresas'].paginator.count+1,2)
        response = self.client.post(path=f'/backoffice/empresas/delete/{self.empresa_to_delete.EmpresaID}',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/empresas')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['empresas'].paginator.count+1,1)

    
    def test_delete_empresa_unauth_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/empresas/delete/{self.other_user.empresa.EmpresaID}',follow=True)
        self.assertEqual(response.status_code,404)


