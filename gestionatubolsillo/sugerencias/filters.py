from django.http import HttpRequest
from users.models import User
from empresas.models import Empresa


def filtra_sugerencias(request:HttpRequest,filter_only_self=False)->tuple[dict,dict]:
    user:User = request.user
    empresa:Empresa = user.empresa
    filtros = {'empresa':empresa}
    exclusiones = {}

    user_creador_id = request.GET.get('usuario_creador_id')
    if filter_only_self:
        filtros['usuario_creador'] = user
    elif user_creador_id:
        user = User.objects.filter(UserID=user_creador_id).first()
        filtros['usuario_creador'] = user

    estado = request.GET.get('estado')
    if estado:
        filtros['estado']=estado
    else:
        exclusiones['estado']= 'borrada'

    id_empresa = request.GET.get('empresa_id')
    if id_empresa:
        empresa = Empresa.objects.filter(EmpresaID=id_empresa).first()
        filtros['empresa']=empresa

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    if fecha_inicio:
        filtros['fecha_creacion__gte'] = fecha_inicio
    if fecha_fin:
        filtros['fecha_creacion__lte'] = fecha_fin

    user_ref_id = request.GET.get('user_ref_id')
    if user_ref_id:
        user = User.objects.filter(UserID=user_ref_id).first()
        filtros['usuario_referente']=user

    return filtros, exclusiones