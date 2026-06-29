from django.http import HttpRequest
from users.models import User
from empresas.models import Empresa

def filtra_empresa(request:HttpRequest)->tuple[dict,dict]:
    user:User = request.user
    empresa_usuario:Empresa = user.empresa
    filtros = {'cuenta_id':user.cuenta.pk}
    exclusiones = {'EmpresaID':empresa_usuario.EmpresaID}

    return filtros, exclusiones
