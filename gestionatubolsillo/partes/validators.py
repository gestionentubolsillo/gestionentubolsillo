from django.http import HttpRequest
from django.contrib import messages
from clientes.models import Cliente
from users.models import User
from servicios.models import Servicio
from centrales.models import Central
from .models import Parte
from django.shortcuts import redirect


def validate_parte_trabajo(request: HttpRequest, cliente_id: int, servicio_id: int, usuario_id: int) -> bool:
    errors = _validate_common_partes(request=request,cliente_id=cliente_id,usuario_id=usuario_id)
    cliente = Cliente.objects.filter(ClienteID=cliente_id).first()
    usuario = User.objects.filter(UserID=usuario_id).first() 
    servicio = Servicio.objects.filter(ServicioID=servicio_id).first()
    if not servicio:
        messages.error(request, "El servicio no existe.", extra_tags='error')
        errors = True
    if servicio.empresa != cliente.empresa:
        messages.error(request, "El servicio no pertenece a la misma empresa que el cliente.", extra_tags='error')
        errors = True
    if usuario.servicios.filter(ServicioID=servicio_id).count() == 0:
        messages.error(request, "El usuario no está asociado al servicio seleccionado.", extra_tags='error')
        errors = True
    if cliente.servicios.filter(ServicioID=servicio_id).count() == 0:
        messages.error(request, "El cliente no está asociado al servicio seleccionado.", extra_tags='error')
        errors = True
    return errors


def validate_linea_parte_trabajo(request:HttpRequest,actividad)->bool:
    errors = False
    if not actividad or actividad == '':
        messages.error(request,"Debe indicar una actividad para el parte", extra_tags='error')
        errors = True
    return errors


def validate_parte_incidencia(request:HttpRequest,cliente_id:int,usuario_id:int,texto:str)->bool:
    errors = _validate_common_partes(request=request,cliente_id=cliente_id,usuario_id=usuario_id)
    if not texto or texto == '':
        messages.error(request,"Debe indicar un motivo de incidencia",extra_tags='error')
        errors = True
    return errors

def validate_parte_acuda(request:HttpRequest,cliente_id:int, usuario_id:int,central_id:int,texto:str)->bool:
    errors = _validate_common_partes(request,cliente_id,usuario_id)
    usuario = User.objects.filter(UserID=usuario_id).first()
    central = Central.objects.filter(CentralID=central_id).first()
    if not central:
        messages.error(request, "La central no existe.", extra_tags='error')
        errors = True
    if central.cuenta != usuario.cuenta:
        messages.error(request,"La central no es válida", extra_tags='error')
        errors = True
    if not texto or texto == '':
        messages.error(request,"Debe indicar una descripción para la acuda",extra_tags='error')
        errors = True
    return errors



def _validate_common_partes(request:HttpRequest,cliente_id:int,usuario_id:int)->bool:
    errors = False
    cliente = Cliente.objects.filter(ClienteID=cliente_id).first()
    if not cliente:
        messages.error(request, "El cliente no existe.", extra_tags='error')
        errors = True
    usuario = User.objects.filter(UserID=usuario_id).first() 
    if not usuario:
        messages.error(request, "El usuario no existe.", extra_tags='error')
        errors = True
    if usuario.empresa != cliente.empresa:
        messages.error(request, "El usuario no pertenece a la misma empresa que el cliente.", extra_tags='error')
        errors = True
    return errors

def validate_auth_parte(request:HttpRequest,parte:Parte, not_found_route:str):
    logged_user : User = request.user
    if not parte:
        messages.error(request, 'No se encontró el informe solicitado.', extra_tags='error')
        return redirect(not_found_route)
    if logged_user.cuenta != parte.cuenta:
        return redirect("/AuthError")
    return None
