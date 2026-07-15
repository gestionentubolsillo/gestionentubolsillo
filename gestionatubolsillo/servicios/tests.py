from home.tests import BaseTests
from .models import Servicio

# Create your tests here.

class ServicioTest(BaseTests):
    def setUp(self):
        super().setUp()

class ServicioTestsView(ServicioTest):
    pass

class ServicioTestsCreate(ServicioTest):
    pass

class ServicioTestsDelete(ServicioTest):
    pass

class ServicioTestsEdit(ServicioTest):
    pass
