from django.contrib.messages import get_messages
from django.http import HttpResponse
from .base import ClienteTest

class ClienteTestsViews(ClienteTest):

    def test_list_clientes(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/clientes',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['clientes'].paginator.count,1)

    def test_view_cliente_possitive(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/clientes/{self.cliente_auth.ClienteID}')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['cliente'].ClienteID,self.cliente_auth.ClienteID)

    def test_view_cliente_unauth_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/clientes/{self.cliente_not_auth.ClienteID}')
        self.assertEqual(response.status_code,302)

    def test_view_cliente_non_existent_fails(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/clientes/999',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/clientes')
        self.assertEqual(response.status_code,200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')
        self.assertEqual(str(messages[0]),"El cliente no existe")

class ClienteTestsCreate(ClienteTest):

    def _assertErrorOnRequest(self,response:HttpResponse):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='clientes/form.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')

    def test_create_cliente_possitive(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/clientes/create',data={
            'nombre':'create__','provincia':'ASD','municipio':'ASD', 'empresa':self.logged_user.empresa.EmpresaID
        },format='json',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/clientes')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['clientes'].paginator.count,2)

    def test_create_cliente_invalid_empresa_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/clientes/create',data={
            'nombre':'error__','provincia':'ASD','municipio':'ASD', 'empresa':''
        },format='json',follow=True)
        self._assertErrorOnRequest(response)

class ClienteTestsDelete(ClienteTest):

    def test_delete_cliente_possitive(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/clientes/delete/{self.cliente_auth.ClienteID}',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/clientes')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['clientes'].paginator.count,0)

    def test_delete_cliente_unauth_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/clientes/delete/{self.cliente_not_auth.ClienteID}',follow=True)
        self.assertEqual(response.status_code,404)