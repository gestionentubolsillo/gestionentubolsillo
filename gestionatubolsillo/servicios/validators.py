from django.http import HttpRequest
from django.contrib import messages
from django.utils.dateparse import parse_time
from django.db.models.manager import BaseManager
from empresas.models import Empresa

from clientes.models import Cliente
from .models import Servicio
from users.models import User
from django.shortcuts import redirect




def validate_servicio(request:HttpRequest,nombre,
                      dias_semana,hora_inicio,hora_fin,empresa_id)->bool:
    errors = False
    try:
        empresa = Empresa.objects.filter(EmpresaID=empresa_id,cuenta=request.user.cuenta).first()
    except ValueError:
        empresa = None
    if nombre == '':
        messages.error(request,"Debe indicar un nombre al servicio",extra_tags='error')
        errors = True
    if dias_semana:
        dias_validos = dict(Servicio._meta.get_field('dias_semana').choices).keys()
        dias_invalidos = [dia for dia in dias_semana if dia not in dias_validos]
        if dias_invalidos:
            messages.error(request,"No se reconocen los días asignados",extra_tags='error')
            errors = True
    if dias_semana and not (hora_inicio or hora_fin):
        messages.error(request,"Debe indicar un horario si ha asignado días",extra_tags='error')
        errors = True
    if not empresa:
        messages.error(request,"Debe indicar la empresa que proporciona el servicio",extra_tags='error')
        errors = True
    try:
        hora_inicio_parsed = parse_time(hora_inicio) if hora_inicio else None
        hora_fin_parsed = parse_time(hora_fin) if hora_fin else None
    except (ValueError,TypeError):
        hora_inicio_parsed = None
        hora_fin_parsed = None
    if hora_inicio and not hora_inicio_parsed:
        messages.error(request,"Debe indicar un formato de horas válido",extra_tags='error')
        errors = True
    if hora_fin and not hora_fin_parsed:
        messages.error(request,"Debe indicar un formato de horas válido",extra_tags='error')
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
