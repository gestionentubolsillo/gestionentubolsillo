from django.http import HttpResponse
from .base_partes import BaseParteTest
from partes.models import Parte_Trabajo,Linea_Parte_Trabajo
from servicios.models import Servicio

class TrabajoTest(BaseParteTest):

    def setUp(self):
        super().setUp()

        servicio_auth = Servicio(cuenta=self.logged_user.cuenta,
            nombre='prueba__',empresa=self.logged_user.empresa)
        servicio_auth.save()

        self.cliente_auth.servicios.set(Servicio.objects.filter(ServicioID=servicio_auth.ServicioID))
        self.logged_user.servicios.set(Servicio.objects.filter(ServicioID=servicio_auth.ServicioID))

        parte_auth = Parte_Trabajo(usuario_creador=self.logged_user,cuenta=self.logged_user.cuenta,
            usuario_asignado=self.logged_user, empresa=self.logged_user.empresa,cliente=self.cliente_auth,
            servicio=servicio_auth)
        parte_auth.save()

        self.parte_auth = parte_auth
        self.servicio_auth = servicio_auth

        servicio_not_auth = Servicio(cuenta=self.other_user.cuenta,
            nombre='notauth__',empresa=self.other_user.empresa)
        servicio_not_auth.save()

        self.cliente_no_auth.servicios.set(Servicio.objects.filter(ServicioID=servicio_not_auth.ServicioID))
        self.other_user.servicios.set(Servicio.objects.filter(ServicioID=servicio_not_auth.ServicioID))

        parte_no_auth = Parte_Trabajo(usuario_creador=self.other_user,cuenta=self.other_user.cuenta,
            usuario_asignado=self.other_user, empresa=self.other_user.empresa,cliente=self.cliente_no_auth,
            servicio=servicio_not_auth)
        parte_no_auth.save()

        self.parte_no_auth = parte_no_auth
        self.servicio_no_auth = servicio_not_auth

class TrabajoTestsView(TrabajoTest):

    def test_list_partes(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/partes_trabajo',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['partes'].paginator.count,1)

    def test_get_parte_possitive(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/partes_trabajo/{self.parte_auth.ParteTrabajoID}',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['parte'].ParteTrabajoID,self.parte_auth.ParteTrabajoID)
        self.assertTemplateUsed(response,template_name='informes/trabajo/form.html')

    def test_get_parte_unauth_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/partes_trabajo/{self.parte_no_auth.ParteTrabajoID}',follow=True)
        self.assertEqual(response.status_code,404)

    def test_get_parte_pdf_preview(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/partes/{self.parte_auth.ParteTrabajoID}',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['parte'].ParteTrabajoID,self.parte_auth.ParteTrabajoID)
        self.assertTemplateUsed(response,template_name='informes/trabajo/pdfview.html')

    def test_get_parte_pdf_preview_unauth_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/partes/{self.parte_no_auth.ParteTrabajoID}',follow=True)
        self.assertEqual(response.status_code,404)

class TrabajoTestsCreateOrModify(TrabajoTest):

    def _assertErrorOnCreation(self,response:HttpResponse):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response,template_name='informes/trabajo/form.html')

    def test_create_parte_possitive(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/partes_trabajo/create',data={
            'usuario_id':self.logged_user.UserID,'cliente_id':self.cliente_auth.ClienteID,'servicio_id':self.servicio_auth.ServicioID
        },format='json',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/partes_trabajo')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['partes'].paginator.count,2)

    def test_create_parte_unauth_user_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/partes_trabajo/create',data={
            'usuario_id':self.other_user.UserID,'cliente_id':self.cliente_auth.ClienteID,'servicio_id':self.servicio_auth.ServicioID
        },format='json',follow=True)
        self._assertErrorOnCreation(response)

    def test_create_parte_parte_unauth_client_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/partes_trabajo/create',data={
            'usuario_id':self.logged_user.UserID,'cliente_id':self.cliente_no_auth.ClienteID,'servicio_id':self.servicio_auth.ServicioID
        },format='json',follow=True)
        self._assertErrorOnCreation(response)

    def test_create_parte_unauth_service_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/partes_trabajo/create',data={
            'usuario_id':self.logged_user.UserID,'cliente_id':self.cliente_auth.ClienteID,'servicio_id':self.servicio_no_auth.ServicioID
        },format='json',follow=True)
        self._assertErrorOnCreation(response)

    def test_create_valid_parte_unauth_cuenta_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/partes_trabajo/create',data={
            'usuario_id':self.other_user.UserID,'cliente_id':self.cliente_no_auth.ClienteID,'servicio_id':self.servicio_no_auth.ServicioID
        },format='json',follow=True)
        self._assertErrorOnCreation(response)

    def test_create_invalid_arguments_fails(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/partes_trabajo/create',data={
            'usuario_id':'','cliente_id':'','servicio_id':''
        },format='json',follow=True)
        self._assertErrorOnCreation(response)

    def test_add_linea_to_parte_possitive(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/partes_trabajo/{self.parte_auth.ParteTrabajoID}/actividades',data={
            'actividad': 'Sin novedad'
        },format='json',follow=True)
        self.assertRedirects(response,expected_url=f'/backoffice/partes_trabajo/{self.parte_auth.ParteTrabajoID}')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['lineas'].count(),1)

    def test_add_linea_invalid_value_to_parte_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/partes_trabajo/{self.parte_auth.ParteTrabajoID}/actividades',data={
            'actividad': 'Invalid__'
        },format='json',follow=True)
        self._assertErrorOnCreation(response)

    def test_add_linea_to_unauth_parte_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/partes_trabajo/{self.parte_no_auth.ParteTrabajoID}/actividades',data={
            'actividad': 'Sin novedad'
        },format='json',follow=True)
        self.assertEqual(response.status_code,404)
        self.assertFalse(Linea_Parte_Trabajo.objects.filter(parte_trabajo=self.parte_no_auth).exists())

    def test_add_relevo_to_parte_possitive(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/partes_trabajo/{self.parte_auth.ParteTrabajoID}/relevar',data={
            'usuario_id':self.logged_user.UserID
        },format='json',follow=True)
        self.assertRedirects(response,expected_url=f'/backoffice/partes/{self.parte_auth.ParteTrabajoID}')
        self.assertEqual(response.status_code,200)
        self.assertTrue(Linea_Parte_Trabajo.objects.filter(parte_trabajo=self.parte_auth,actividad='Relevo').exists())

    def test_add_relevo_to_parte_unauth_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/partes_trabajo/{self.parte_no_auth.ParteTrabajoID}/relevar',data={
            'usuario_id':self.other_user.UserID
        },format='json',follow=True)
        self.assertEqual(response.status_code,404)
        self.assertFalse(Linea_Parte_Trabajo.objects.filter(parte_trabajo=self.parte_no_auth,actividad='Relevo').exists())

    def test_close_parte_possitive(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/partes_trabajo/{self.parte_auth.ParteTrabajoID}/close',follow=True)
        self.assertRedirects(response,expected_url=f'/backoffice/partes/{self.parte_auth.ParteTrabajoID}')
        self.assertEqual(response.status_code,200)
        self.assertTrue(Linea_Parte_Trabajo.objects.filter(parte_trabajo=self.parte_auth,actividad='Finalización').exists())

    def test_close_parte_unauth_fails(self):
        self.assertLogin()
        response = self.client.post(path=f'/backoffice/partes_trabajo/{self.parte_no_auth.ParteTrabajoID}/close',follow=True)
        self.assertEqual(response.status_code,404)
        self.assertFalse(Linea_Parte_Trabajo.objects.filter(parte_trabajo=self.parte_no_auth,actividad='Finalización').exists())
