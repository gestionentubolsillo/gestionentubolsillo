from django.http import HttpResponse
from home.tests import BaseTests
from .models import Tarea, ListadoUsers
from users.models import User

# Create your tests here.

class TareaTest(BaseTests):
    def setUp(self):
        super().setUp()
        tarea_logged_user = Tarea(cuenta=self.logged_user.cuenta,
            texto='prueba__',usuario_creador=self.logged_user,
            usuario_asignado=self.logged_user)
        tarea_logged_user.save()

        self.tarea_logged_user = tarea_logged_user

        tarea_other_user = Tarea(cuenta=self.other_user.cuenta,
            texto='other__',usuario_creador=self.other_user,
            usuario_asignado=self.other_user)
        tarea_other_user.save()

        self.tarea_other_user = tarea_other_user

class TareaTestsView(TareaTest):

    def test_list_view_possitive(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/tareas')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['tareas'].paginator.count,1)

    def test_view_tarea_possitive(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/tareas/{self.tarea_logged_user.TareaID}')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['tarea'].TareaID,self.tarea_logged_user.TareaID)

    def test_view_unauth_tarea_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/tareas/{self.tarea_other_user.TareaID}')
        self.assertEqual(response.status_code,302)


class TareaTestsCreate(TareaTest):

    def setUp(self):
        super().setUp()
        lista_users = ListadoUsers(cuenta=self.logged_user.cuenta,nombre='allowed__')
        lista_users.save()
        lista_users.usuarios.set(User.objects.filter(UserID=self.logged_user.UserID))

        self.lista_users = lista_users

        lista_not_auth = ListadoUsers(cuenta=self.other_user.cuenta,nombre='unauthorized__')
        lista_not_auth.save()
        lista_not_auth.usuarios.set(User.objects.filter(UserID=self.other_user.UserID))

        self.lista_not_auth = lista_not_auth

    def _assertNotChangesInTarea(self,response:HttpResponse):
        self.assertRedirects(response,expected_url='/backoffice/tareas')
        self.assertEqual(response.context['tareas'].paginator.count,1)
        self.assertFalse(Tarea.objects.filter(texto='notauth__').exists())
    
    def test_create_tarea_possitive_empresas(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/tareas/create',data={
            'texto':'textoprueba__','is_urgent':'Normal','empresas_ids':[self.logged_user.empresa.EmpresaID]
        },format='json',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/tareas')
        self.assertEqual(response.context['tareas'].paginator.count,2)

    def test_create_tarea_possitive_lista_users(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/tareas/create',data={
            'texto':'textoprueba__','is_urgent':'Normal','listas_ids':[self.lista_users.pk]
        },format='json',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/tareas')
        self.assertEqual(response.context['tareas'].paginator.count,2)

    def test_create_tarea_possitive_users(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/tareas/create',data={
            'texto':'textoprueba__','is_urgent':'Normal','users_id':[self.logged_user.UserID]
        },format='json',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/tareas')
        self.assertEqual(response.context['tareas'].paginator.count,2)

    def test_create_tarea_fails_empresa_not_auth(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/tareas/create',data={
            'texto':'notauth__','is_urgent':'Normal','empresas_ids':[self.other_user.empresa.EmpresaID]
        },format='json',follow=True)
        self._assertNotChangesInTarea(response)

    def test_create_tarea_fails_lista_not_auth(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/tareas/create',data={
            'texto':'notauth__','is_urgent':'Normal','listas_ids':[self.lista_not_auth.pk]
        },format='json',follow=True)
        self._assertNotChangesInTarea(response)
        

    def test_create_tarea_fails_users_not_auth(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/tareas/create',data={
            'texto':'notauth__','is_urgent':'Normal','users_id':[self.other_user.UserID]
        },format='json',follow=True)
        self._assertNotChangesInTarea(response)

    def test_create_tarea_fails_empresa_unexpected_values(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/tareas/create',data={
            'texto':'invalid__','is_urgent':'Normal','empresas_ids':['','.']
        },format='json',follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='tareas/form.html')
        self.assertFalse(Tarea.objects.filter(texto='invalid__').exists())

    def test_create_tarea_fails_lista_unexpected_values(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/tareas/create',data={
            'texto':'invalid__','is_urgent':'Normal','listas_ids':['','.']
        },format='json',follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='tareas/form.html')
        self.assertFalse(Tarea.objects.filter(texto='invalid__').exists())

    def test_create_tarea_fails_users_unexpected_values(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/tareas/create',data={
            'texto':'invalid__','is_urgent':'Normal','users_id':['','.']
        },format='json',follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='tareas/form.html')
        self.assertFalse(Tarea.objects.filter(texto='invalid__').exists())


class TareaTestsDelete(TareaTest):
    
    def test_delete_tarea_possitive(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/tareas/{self.tarea_logged_user.TareaID}/delete',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/tareas')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['tareas'].paginator.count,0)

    def test_delete_tarea_unauth_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/tareas/{self.tarea_other_user.TareaID}/delete',follow=True)
        self.assertEqual(response.status_code,404)

class TareaTestsEdit(TareaTest):
    #De momento no hay edicion de tareas
    pass
