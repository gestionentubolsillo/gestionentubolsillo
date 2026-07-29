from .base_partes import BaseParteTest
from partes.models import Informe_Acuda
from centrales.models import Central

class AcudaTest(BaseParteTest):

    def setUp(self):
        super().setUp()

        central_auth = Central(nombre='prueba__',
            usuario_creador=self.logged_user,cuenta=self.logged_user.cuenta)
        central_auth.save()
        self.central_auth = central_auth
        
        central_no_auth = Central(nombre='notauth__',
            usuario_creador=self.other_user,cuenta=self.other_user.cuenta)
        central_no_auth.save()
        self.central_no_auth = central_no_auth

        acuda_auth = Informe_Acuda(usuario_creador=self.logged_user,cuenta=self.logged_user.cuenta,
            usuario_asignado=self.logged_user, empresa=self.logged_user.empresa,cliente=self.cliente_auth,central=self.central_auth)
        acuda_auth.save()
        self.acuda_auth = acuda_auth

        acuda_no_auth = Informe_Acuda(usuario_creador=self.other_user,cuenta=self.other_user.cuenta,
            usuario_asignado=self.other_user, empresa=self.other_user.empresa,cliente=self.cliente_no_auth,central=self.central_no_auth)
        acuda_no_auth.save()
        self.acuda_no_auth = acuda_no_auth

class AcudaTestsView(AcudaTest):

    def test_list_acudas(self):
        self.assertLogin()
        response = self.client.get(path='/backoffice/informes_acuda',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['partes'].paginator.count,1)

    def test_get_acuda_possitive(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/informes_acuda/{self.acuda_auth.InformeAcudaID}',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['parte'].InformeAcudaID,self.acuda_auth.InformeAcudaID)
        self.assertTemplateUsed(response,template_name='informes/acuda/form.html')

    def test_get_acuda_unauth_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/informes_acuda/{self.acuda_no_auth.InformeAcudaID}',follow=True)
        self.assertEqual(response.status_code,404)

    def test_get_acuda_pdf_preview(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/acudas/{self.acuda_auth.InformeAcudaID}',follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['parte'].InformeAcudaID,self.acuda_auth.InformeAcudaID)
        self.assertTemplateUsed(response,template_name='informes/acuda/pdfview.html')

    def test_get_acuda_pdf_preview_unauth_fails(self):
        self.assertLogin()
        response = self.client.get(path=f'/backoffice/acudas/{self.acuda_no_auth.InformeAcudaID}',follow=True)
        self.assertEqual(response.status_code,404)

class AcudaTestsCreate(AcudaTest):

    def test_create_acuda_possitive(self):
        self.assertLogin()
        response = self.client.post(path='/backoffice/informes_acuda/create',data={
            'cliente_id':self.cliente_auth.ClienteID,'usuario_id':self.logged_user.UserID,
            'central_id':self.central_auth.CentralID,'descripcion':'create__'
        },format='json',follow=True)
        self.assertRedirects(response,expected_url='/backoffice/informes_acuda')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['partes'].paginator.count,2)