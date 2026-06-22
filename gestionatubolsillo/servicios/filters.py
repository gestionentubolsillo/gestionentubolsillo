from django.http import HttpRequest
from users.models import User
from empresas.models import Empresa


def filtra_servicios(request:HttpRequest,show_deleted=False)->tuple[dict,dict]:
    user:User = request.user
    empresa:Empresa = user.empresa
    filtro_empresa = request.GET.get('empresa',empresa.EmpresaID)
    filtros={'empresa_id':filtro_empresa}
    #TODO: modificar para no mostrar los borrados
    exclusiones={} if not show_deleted else {}
    return filtros,exclusiones