from django.http import HttpRequest
from empresas.models import Empresa
from clientes.models import Cliente
from servicios.models import Servicio
from centrales.models import Central
from users.models import User

def _filter_parte(request:HttpRequest)-> tuple[dict, dict]:
    user : User = request.user
    empresa : Empresa = user.empresa
    filtro_empresa = request.GET.get('empresa', empresa.EmpresaID)
    filtros = {'cuenta': user.cuenta, 'empresa': filtro_empresa}
    exclusiones = {}

    filtro_fecha_inicio = request.GET.get('fecha_inicio')
    filtro_fecha_fin = request.GET.get('fecha_fin')
    if filtro_fecha_inicio:
        filtros['fecha_creacion__gte'] = filtro_fecha_inicio
    if filtro_fecha_fin:
        filtros['fecha_finalizacion__lte'] = filtro_fecha_fin

    usuario_asignado_id = request.GET.get('usuario_asignado_id')
    if usuario_asignado_id:
        usuario_asignado = User.objects.filter(UserID=usuario_asignado_id).first()
        filtros['usuario_asignado'] = usuario_asignado
    
    cliente_id = request.GET.get('cliente_id')
    if cliente_id:
        cliente = Cliente.objects.filter(ClienteID=cliente_id).first()
        filtros['cliente'] = cliente

    return filtros, exclusiones


def filtra_partes_trabajo(request:HttpRequest)-> tuple[dict, dict, list]:
    """
    Constructor de filtros y exclusiones para 
    Queries de objetos de `Parte_Trabajo`
    a partir de los parámetros GET de la request.

    Params
    ----------------------------------------------------
    request: HttpRequest
        - empresa: Default request.user.empresa
        - fecha_inicio: nullable
        - fecha_fin: nullable
        - usuario_asignado_id: nullable
        - cliente_id: nullable
        - servicio_id: nullable

    Return
    ----------------------------------------------------
    tuple[dict,dict,dict]
        (filtros,exclusiones):
        - filtros: **kwargs a pasar a Query.filter()
        - exclusiones: **kwargs a pasar a Query.exclude()
        - related: *args a pasar a Query.select_related() para evitar problemas de Queries N+1
    """
    filtros, exclusiones = _filter_parte(request)

    servicio_id = request.GET.get('servicio_id')
    if servicio_id:
        servicio = Servicio.objects.filter(ServicioID=servicio_id).first()
        filtros['servicio'] = servicio

    related_fields = ['servicio','usuario_asignado','cliente']

    return filtros, exclusiones, related_fields

def filtra_partes_incidencia(request:HttpRequest)-> tuple[dict, dict]:
    return _filter_parte(request)

def filtra_partes_inspeccion(request:HttpRequest)-> tuple[dict, dict]:
    return _filter_parte(request)

def filtra_informes_acuda(request:HttpRequest)-> tuple[dict, dict]:
    filtros, exclusiones = _filter_parte(request)
    central_id = request.GET.get('central_id')
    if central_id:
        central = Central.objects.filter(CentralID=central_id).first()
        filtros['central'] = central
    return filtros, exclusiones

