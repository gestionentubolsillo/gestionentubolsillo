from django.http import HttpResponse
from django.contrib.messages import get_messages

from users.models import User
from empresas.models import Empresa

from .base_test import BaseTests

class UserTestsView(BaseTests):
    def test_logged_user_list_users(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/users')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['usuarios'].paginator.count,1)

    def test_logged_user_tries_view_own_details(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/users/{self.logged_user.UserID}')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['usuario'].UserID,self.logged_user.UserID)

    def test_logged_user_tries_view_unauth_user(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/users/{self.other_user.UserID}')
        #self.assertRedirects(response,expected_url='/AuthError')
        self.assertEqual(response.status_code,302)

    def test_logged_user_tries_view_non_existent_user(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/users/{999}')
        self.assertRedirects(response,expected_url='/backoffice/users')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages),1)
        self.assertEqual(str(messages[0]),"El usuario no existe")
        self.assertEqual(messages[0].extra_tags,'error')


class UserTestsCreate(BaseTests):

    def _assertErrorCreateUser(self,response:HttpResponse):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='account/users/form.html')
        self.assertFalse(User.objects.filter(username='error__').exists())

    def test_logged_user_creates_new_user_positive(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/users/create',data={
            'username':'testing__','password':'12345678','password_confirm':'12345678',
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'','provincia':'Sevilla','municipio':'Sevilla','empresa':self.logged_user.empresa.EmpresaID
        },format='json',follow=True)
        user = User.objects.get(username='testing__')
        self.assertRedirects(response,expected_url=f'/backoffice/users/{user.UserID}')
        self.assertEqual(response.status_code,200)

    def test_logged_user_creates_new_user_with_error_passwords_dont_match(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/users/create',data={
            'username':'error__','password':'12345578','password_confirm':'12345678',
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'','provincia':'Sevilla','municipio':'Sevilla','empresa':self.logged_user.empresa.EmpresaID
        },format='json',follow=True)
        self._assertErrorCreateUser(response)

    def test_logged_user_creates_new_user_with_error_password_too_short(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/users/create',data={
            'username':'error__','password':'1578','password_confirm':'1578',
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'','provincia':'ASD','municipio':'ASD','empresa':self.logged_user.empresa.EmpresaID
        },format='json',follow=True)
        self._assertErrorCreateUser(response)

    def test_logged_user_creates_new_user_with_error_name_non_valid(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/users/create',data={
            'username':'error__','password':'12345678','password_confirm':'12345678',
            'nombre':'','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'','provincia':'ASD','municipio':'ASD','empresa':self.logged_user.empresa.EmpresaID
        },format='json',follow=True)
        self._assertErrorCreateUser(response)

    def test_logged_user_creates_new_user_with_error_surname_non_valid(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/users/create',data={
            'username':'error__','password':'12345678','password_confirm':'12345678',
            'nombre':'Alice','apellidos':'','mail':'example@mail.com',
            'direccion':'','provincia':'ASD','municipio':'ASD','empresa':self.logged_user.empresa.EmpresaID
        },format='json',follow=True)
        self._assertErrorCreateUser(response)

    def test_logged_user_creates_new_user_with_error_provincia_non_valid(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/users/create',data={
            'username':'error__','password':'12345678','password_confirm':'12345678',
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'','provincia':'','municipio':'ASD','empresa':self.logged_user.empresa.EmpresaID
        },format='json',follow=True)
        self._assertErrorCreateUser(response)

    def test_logged_user_creates_new_user_with_error_municipio_non_valid(self):   
        self.assertLogin()
        response = self.client.post(path='/backoffice/users/create',data={
            'username':'error__','password':'12345678','password_confirm':'12345678',
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'','provincia':'ASD','municipio':'','empresa':self.logged_user.empresa.EmpresaID
        },format='json',follow=True)
        self._assertErrorCreateUser(response)

    def test_logged_user_creates_new_user_with_error_ValueError_empresa_id(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/users/create',data={
            'username':'error__','password':'12345678','password_confirm':'12345678',
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'','provincia':'ASD','municipio':'ASD','empresa':''
        },format='json',follow=True)
        self._assertErrorCreateUser(response)

    def test_logged_user_creates_new_user_with_error_empresa_id_not_match_any_empresa(self):
        self.assertLogin()   
        response = self.client.post(path='/backoffice/users/create',data={
            'username':'error__','password':'12345678','password_confirm':'12345678',
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'','provincia':'ASD','municipio':'ASD','empresa':999
        },format='json',follow=True)
        self._assertErrorCreateUser(response)

    def test_logged_user_creates_new_user_with_error_empresa_id_not_match_users_cuenta(self):
        self.assertLogin()   
        response = self.client.post(path='/backoffice/users/create',data={
            'username':'error__','password':'12345678','password_confirm':'12345678',
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'','provincia':'ASD','municipio':'ASD','empresa':self.other_user.empresa.EmpresaID
        },format='json',follow=True)
        self._assertErrorCreateUser(response)


class UserTestsDelete(BaseTests):
    def setUp(self):
        super().setUp()
        user_to_delete = User.objects.create_user(
            username='todelete__',email='example@mail.com',password='12345',
            **{'first_name':'Bob','last_name':'Doe','provincia':'ASD','municipio':'ASD',
                          'empresa':self.logged_user.empresa,'cuenta':self.logged_user.cuenta})
        self.user_to_delete = user_to_delete

    def test_logged_user_deletes_user_possitive(self):
        self.assertLogin()
        #Before Deletion
        response = self.client.get(path='/backoffice/users')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['usuarios'].paginator.count,2)
        response = self.client.post(path=f'/backoffice/users/delete/{self.user_to_delete.UserID}', follow=True)
        #After Deletion
        self.assertRedirects(response,expected_url='/backoffice/users')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['usuarios'].paginator.count,1)

    def test_logged_user_tries_delete_unauth_user(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/delete/{self.other_user.UserID}', follow=True)
        #self.assertRedirects(response,expected_url='/AuthError')
        self.assertEqual(response.status_code,404)

    def test_logged_user_tries_delete_non_existent_user(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/delete/{self.other_user.UserID}', follow=True)
        #self.assertRedirects(response,expected_url='/AuthError')
        self.assertEqual(response.status_code,404)

    def test_logged_user_tries_delete_by_GET_method_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/users/delete/{self.user_to_delete.UserID}', follow=True)
        self.assertEqual(response.status_code,405)


class UserTestsEdit(BaseTests):

    def setUp(self):
        super().setUp()
        user_to_edit = User.objects.create_user(
            username='toedit__',email='example@mail.com',password='12345',
            **{'first_name':'Bob','last_name':'Doe','provincia':'ASD','municipio':'ASD',
                          'empresa':self.logged_user.empresa,'cuenta':self.logged_user.cuenta})
        self.user_to_edit = user_to_edit

        new_empresa = Empresa(cuenta=self.user_to_edit.cuenta,nombre='editing empresa',
            paquete='auxiliares',
            usuario_creador=self.logged_user)
        new_empresa.save()
        self.new_empresa = new_empresa

    def _assertErrorEditUser(self,response:HttpResponse):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='account/users/form.html')
        self.assertFalse(User.objects.filter(username='error__').exists())

    def test_logged_user_tries_edit_user_possitive(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/edit/{self.user_to_edit.UserID}',data={
            'username':self.user_to_edit.username,
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'ASF','provincia':'ASF','municipio':'ASF','empresa':self.new_empresa.EmpresaID
        },format='json',follow=True)
        self.assertRedirects(response,expected_url=f'/backoffice/users/{self.user_to_edit.UserID}')
        self.assertEqual(response.status_code,200)
        #After Editing
        self.user_to_edit.refresh_from_db()
        self.assertEqual(self.user_to_edit.empresa,self.new_empresa)
        self.assertEqual(self.user_to_edit.first_name,'Alice')
        self.assertEqual(self.user_to_edit.direccion,'ASF')
        self.assertEqual(self.user_to_edit.provincia,'ASF')
        self.assertEqual(self.user_to_edit.municipio,'ASF')

    def test_logged_user_get_edit_form_possitive(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/users/edit/{self.user_to_edit.UserID}',follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='account/users/form.html')

    def test_logged_user_tries_edit_user_with_error_username_non_valid(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/edit/{self.user_to_edit.UserID}',data={
            'username':'',
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'ASF','provincia':'ASF','municipio':'ASF','empresa':self.new_empresa.EmpresaID
        },format='json',follow=True)
        self._assertErrorEditUser(response)

    def test_logged_user_tries_edit_user_with_error_name_non_valid(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/edit/{self.user_to_edit.UserID}',data={
            'username':self.user_to_edit.username,
            'nombre':'','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'ASF','provincia':'ASF','municipio':'ASF','empresa':self.new_empresa.EmpresaID
        },format='json',follow=True)
        self._assertErrorEditUser(response)

    def test_logged_user_tries_edit_user_with_error_surname_non_valid(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/edit/{self.user_to_edit.UserID}',data={
            'username':self.user_to_edit.username,
            'nombre':'Alice','apellidos':'','mail':'example@mail.com',
            'direccion':'ASF','provincia':'ASF','municipio':'ASF','empresa':self.new_empresa.EmpresaID
        },format='json',follow=True)
        self._assertErrorEditUser(response)
    
    def test_logged_user_tries_edit_user_with_error_provincia_non_valid(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/edit/{self.user_to_edit.UserID}',data={
            'username':self.user_to_edit.username,
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'ASF','provincia':'','municipio':'ASF','empresa':self.new_empresa.EmpresaID
        },format='json',follow=True)
        self._assertErrorEditUser(response)

    def test_logged_user_tries_edit_user_with_error_municipio_non_valid(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/edit/{self.user_to_edit.UserID}',data={
            'username':self.user_to_edit.username,
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'ASF','provincia':'ASF','municipio':'','empresa':self.new_empresa.EmpresaID
        },format='json',follow=True)
        self._assertErrorEditUser(response)
        
    def test_logged_user_tries_edit_user_with_error_ValueError_empresa_id(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/edit/{self.user_to_edit.UserID}',data={
            'username':self.user_to_edit.username,
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'ASF','provincia':'ASF','municipio':'ASF','empresa':''
        },format='json',follow=True)
        self._assertErrorEditUser(response)

    def test_logged_user_tries_edit_user_with_error_empresa_id_not_match_any_empresa(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/edit/{self.user_to_edit.UserID}',data={
            'username':self.user_to_edit.username,
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'ASF','provincia':'ASF','municipio':'ASF','empresa':999
        },format='json',follow=True)
        self._assertErrorEditUser(response)

    def test_logged_user_tries_edit_user_with_error_empresa_cuenta_does_not_match_users_cuenta(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/users/edit/{self.user_to_edit.UserID}',data={
            'username':self.user_to_edit.username,
            'nombre':'Alice','apellidos':'Doe','mail':'example@mail.com',
            'direccion':'ASF','provincia':'ASF','municipio':'ASF','empresa':self.other_user.empresa.EmpresaID
        },format='json',follow=True)
        self._assertErrorEditUser(response)


        

    
