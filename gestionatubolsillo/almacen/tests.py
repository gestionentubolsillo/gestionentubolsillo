from django.http import HttpResponse
from django.contrib.messages import get_messages
from home.tests import BaseTests
from .models import Almacen_Item
from decimal import Decimal

# Create your tests here.
class AlmacenTest(BaseTests):

    def setUp(self):
        super().setUp()

        item_auth = Almacen_Item(nombre='prueba__',
            usuario_creador=self.logged_user,cuenta=self.logged_user.cuenta)
        item_auth.save()
        self.item_auth = item_auth

        item_not_auth = Almacen_Item(nombre='notauth__',
            usuario_creador = self.other_user,cuenta=self.other_user.cuenta)
        item_not_auth.save()
        self.item_not_auth = item_not_auth

class AlmacenTestsView(AlmacenTest):

    def test_list_possitive(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/almacen',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['almacen_items'].paginator.count,1)

    def test_get_item_possitive(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/almacen/{self.item_auth.AlmacenID}',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['almacen_item'].AlmacenID,self.item_auth.AlmacenID)

    def test_get_item_unauth_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/almacen/{self.item_not_auth.AlmacenID}')
        self.assertEqual(response.status_code,302)

    def test_get_item_non_existent_fails(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/almacen/999',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/almacen')
        self.assertEqual(response.status_code,200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')
        self.assertFalse(Almacen_Item.objects.filter(nombre='error__').exists())

class AlmacenTestsCreate(AlmacenTest):

    def _assertErrorOnCreate(self,response:HttpResponse):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='almacen/form.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0].extra_tags,'error')

    def test_create_item_possitive(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/almacen/create',data={
            'nombre':'create__','stock':20,'precio_unitario':4.99
        },format='json',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/almacen')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['almacen_items'].paginator.count,2)
        #Check there is not any floating point aprox.
        item = Almacen_Item.objects.filter(nombre='create__').first()
        self.assertEqual(item.precio_unitario,Decimal('4.99'))

    def test_create_item_negative_stock_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/almacen/create',data={
            'nombre':'error__','stock':-1,'precio_unitario':4.99
        },format='json',follow=True)
        self._assertErrorOnCreate(response)

    def test_create_item_negative_price_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/almacen/create',data={
            'nombre':'error__','stock':20,'precio_unitario':-4.99
        },format='json',follow=True)
        self._assertErrorOnCreate(response)

class AlmacenTestsDelete(AlmacenTest):

    def test_delete_item_possitive(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/almacen/delete/{self.item_auth.AlmacenID}',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/almacen')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['almacen_items'].paginator.count,0)

    def test_delete_item_unauth_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/almacen/delete/{self.item_not_auth.AlmacenID}',follow=True)
        self.assertEqual(response.status_code,404)

