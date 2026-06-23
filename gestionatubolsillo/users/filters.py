from django.http import HttpRequest
from .models import User
from empresas.models import Empresa

def filter_users(request:HttpRequest)->tuple[dict,dict]:
    usuario : User = request.user
    empresa_de_usuario :Empresa = usuario.empresa
    filtro_empresa = request.GET.get('empresa',empresa_de_usuario.EmpresaID)
    filtros = {'empresa_id':filtro_empresa}
    exclusiones = {}
    return filtros,exclusiones