from django.http import HttpRequest
from django.contrib import messages
from django.db.models.manager import BaseManager
from empresas.models import Empresa

from clientes.models import Cliente




def validate_servicio(request:HttpRequest,nombre,
                      dias_semana,hora_inicio,hora_fin,empresa_id)->bool:
    errors = False
    empresa = Empresa.objects.filter(EmpresaID=empresa_id).first()
    if nombre == '':
        messages.error(request,"Debe indicar un nombre al servicio",extra_tags='error')
        errors = True
    if dias_semana and not (hora_inicio or hora_fin):
        messages.error(request,"Debe indicar un horario si ha asignado días",extra_tags='error')
        errors = True
    if not empresa:
        messages.error(request,"Debe indicar la empresa que proporciona el servicio",extra_tags='error')
        errors = True
    return errors


def validate_clientes_servicio(request:HttpRequest, clientes_ids,allowed_clients_to_add:BaseManager[Cliente])->bool:
    errors = False
    if not clientes_ids:
        messages.error(request, "Debe seleccionar al menos un cliente", extra_tags='error')
        errors = True
    clientes = Cliente.objects.filter(ClienteID__in=clientes_ids)
    if not clientes:
        messages.error(request, "No se ha podido encontrar ningún cliente", extra_tags='error')
        errors = True
    clientes_no_permitidos = clientes.difference(allowed_clients_to_add)
    if clientes_no_permitidos.exists():
        messages.error(request, "No puede añadir o eliminar clientes no autorizados a este servicio", extra_tags='error')
        errors = True
    return errors