from django.http import HttpRequest
from django.contrib import messages
from django.db.models.manager import BaseManager

from empresas.models import Empresa
from servicios.models import Servicio
from .models import Cliente, user_client
from users.models import User

from django.shortcuts import redirect

MIN_CHARS_PASSWORD = 8

def validate_client(request:HttpRequest,nombre,provincia,municipio,empresa_id)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe proporcionarle un nombre al cliente", extra_tags='error')
        errors = True
    if provincia == '' or municipio == '':
        messages.error(request,"Debe indicar provincia y municipio al que pertenece",extra_tags='error')
        errors = True
    empresa = Empresa.objects.filter(EmpresaID=empresa_id).first()
    if empresa is None:
        messages.error(request,"Debe indicar una empresa válida",extra_tags='error')
        errors = True
    return errors


def validate_user_client(request:HttpRequest,username,password)->bool:
    errors = False
    if username == '' or password == '':
        messages.error(request,"Debe rellenar credenciales de nombre de usuario y contraseña",extra_tags='error')
        errors = True
    global MIN_CHARS_PASSWORD
    if len(password) < MIN_CHARS_PASSWORD:
        messages.error(request,f"La contraseña debe tener al menos {MIN_CHARS_PASSWORD} caracteres",extra_tags='error')
        errors = True
    return errors

def validate_servicios_cliente(request:HttpRequest,servicios_ids,allowed_services_to_add:BaseManager[Servicio])->bool:
    errors = False
    if not servicios_ids:
        messages.error(request, "Debe seleccionar al menos un servicio", extra_tags='error')
        errors = True
    servicios = Servicio.objects.filter(ServicioID__in=servicios_ids)
    if not servicios:
        messages.error(request, "No se ha podido encontrar ningún servicio", extra_tags='error')
        errors = True
    servicios_no_permitidos = servicios.difference(allowed_services_to_add)
    if servicios_no_permitidos.exists():
        messages.error(request, "No puede añadir servicios no autorizados a este cliente", extra_tags='error')
        errors = True
    return errors

def can_client_access_user_cli(request:HttpRequest,cliente:Cliente,user_cli:user_client)->bool:
    errors = False
    if not cliente:
        messages.error(request,"El cliente proporcionado no existe",extra_tags='error')
        errors = True
    if not user_cli:
        messages.error(request,"El usuario proporcionado al cliente no existe",extra_tags='error')
        errors = True
    if cliente != user_cli.cliente:
        messages.error(request,"Acceso inválido, no tiene acceso al usuario requerido",extra_tags='error')
        errors = True
    return errors


def validate_auth_client(request:HttpRequest,cliente:Cliente):
    logged_user : User = request.user
    if not cliente:
        messages.error(request,"El cliente no existe",extra_tags='error')
        return redirect('/backoffice/clientes')
    if logged_user.cuenta != cliente.cuenta:
        return redirect('/AuthError')
    return None