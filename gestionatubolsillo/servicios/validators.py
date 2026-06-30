from django.http import HttpRequest
from django.contrib import messages
from django.db.models.manager import BaseManager
from empresas.models import Empresa

from clientes.models import Cliente
from .models import Servicio
from users.models import User
from django.shortcuts import redirect




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

def validate_auth_servicio(request:HttpRequest,servicio:Servicio):
    if not servicio:
        messages.error(request,"El servicio no existe",extra_tags='error')
        return redirect('/backoffice/servicios')
    logged_user : User = request.user
    if logged_user.cuenta != servicio.cuenta:
        return redirect("/AuthError")
    return None
