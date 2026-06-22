from django.http import HttpRequest
from django.contrib import messages
from django.db.models.manager import BaseManager

from empresas.models import Empresa
from servicios.models import Servicio

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