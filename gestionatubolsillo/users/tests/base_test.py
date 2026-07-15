from django.test import TestCase

from users.models import User, PermisosModulo, Cuenta
from empresas.models import Empresa

class BaseTests(TestCase):
    def setUp(self)->None:
        cuenta_logged_user = Cuenta()
        cuenta_logged_user.save()

        cuenta_other_user = Cuenta()
        cuenta_other_user.save()

        logged_user = User(
            username='test_user',
            email='',
            nif='12345678',
            first_name='jhon',
            last_name='doe',
            direccion='',
            provincia='',
            municipio='',
            categoria='',
            esInspector=True,
            esInspector_parteTrabajo=True,
            has_login_access=True,
            has_dashboard_access=True,
            can_view_own_partes_trabajo=True,
            always_track_GPS=True,
            is_admin=True,
            precio_hora=5.50,
            cuenta=cuenta_logged_user

        )
        logged_user.set_password('12345')
        logged_user.save()
        empresa_logged_user = Empresa(
            cuenta=cuenta_logged_user,
            nombre='testing empresa',
            paquete='seguridad',
            usuario_creador=logged_user
        )
        empresa_logged_user.save()
        logged_user.empresa = empresa_logged_user
        logged_user.save()

        PermisosModulo.objects.bulk_create(
            PermisosModulo(user=logged_user, modulo=modulo, nivel='2')
            for modulo, _ in PermisosModulo._meta.get_field('modulo').choices
        )

        self.logged_user = logged_user

        other_user = User(
            username='test_other',
            email='',
            nif='56432127',
            first_name='jane',
            last_name='doe',
            direccion='',
            provincia='',
            municipio='',
            categoria='',
            esInspector=True,
            esInspector_parteTrabajo=True,
            has_login_access=True,
            has_dashboard_access=True,
            can_view_own_partes_trabajo=True,
            always_track_GPS=True,
            is_admin=True,
            precio_hora=5.50,
            cuenta=cuenta_other_user
        )
        other_user.set_password('12345')
        other_user.save()

        empresa_other_user = Empresa(
            cuenta=cuenta_other_user,
            nombre='testing empresa',
            paquete='seguridad',
            usuario_creador=other_user
        )
        empresa_other_user.save()
        other_user.empresa = empresa_other_user
        other_user.save()

        PermisosModulo.objects.bulk_create(
            PermisosModulo(user=other_user, modulo=modulo, nivel='2')
            for modulo, _ in PermisosModulo._meta.get_field('modulo').choices
        )

        self.other_user = other_user

    def assertLogin(self):
        response = self.client.post(path='/login',data={'username':'test_user','password':'12345'},format='json', follow=True)
        self.assertRedirects(response,expected_url='/')
        self.assertEqual(response.status_code,200)