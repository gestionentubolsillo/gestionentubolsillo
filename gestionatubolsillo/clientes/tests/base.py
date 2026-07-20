from home.tests import BaseTests
from clientes.models import Cliente

class ClienteTest(BaseTests):

    def setUp(self):
        super().setUp()

        cliente_auth = Cliente(nombre='prueba__',
            empresa=self.logged_user.empresa,cuenta=self.logged_user.cuenta)
        cliente_auth.save()
        self.cliente_auth = cliente_auth

        cliente_not_auth = Cliente(nombre='notauth__',
            empresa=self.other_user.empresa,cuenta=self.other_user.cuenta)
        cliente_not_auth.save()
        self.cliente_not_auth = cliente_not_auth
