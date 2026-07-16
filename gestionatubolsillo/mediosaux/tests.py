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
