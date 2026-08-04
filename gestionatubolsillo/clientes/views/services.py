from django.shortcuts import redirect
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpRequest
from django.views.decorators.http import require_POST, require_http_methods

from enum import Enum

from clientes.models import Cliente
from servicios.models import Servicio, can_CRUD_servicios
from users.models import can_access_backoffice
from empresas.models import Empresa

from clientes.validators import validate_servicios_cliente, validate_auth_client
from auditloggers.handlers import save_log

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
@require_http_methods(["GET","POST"])
def add_servicios_to_cliente(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(ClienteID=client_id).first()
    auth_error = validate_auth_client(request,cliente)
    if auth_error:
        save_log(request, apartado='CLIENTE', accion='UNAUTH', id_user=request.user.pk, id_cuenta=cliente.cuenta.pk,info=f'Intento de agregar servicios a cliente con ID: {cliente.ClienteID} sin autorización')
        return auth_error
    return _change_servicios_de_cliente(request,cliente,action=ClienteAccionServicios.ADD)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
@require_POST
def remove_servicios_to_cliente(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(ClienteID=client_id).first()
    auth_error = validate_auth_client(request,cliente)
    if auth_error:
        save_log(request, apartado='CLIENTE', accion='UNAUTH', id_user=request.user.pk, id_cuenta=cliente.cuenta.pk,info=f'Intento de eliminar servicios a cliente con ID: {cliente.ClienteID} sin autorización')
        return auth_error
    return _change_servicios_de_cliente(request,cliente,action=ClienteAccionServicios.REMOVE)

class ClienteAccionServicios(Enum):
    ADD = 'add',
    REMOVE = 'remove'

def _change_servicios_de_cliente(request:HttpRequest,cliente:Cliente,action:ClienteAccionServicios):
    
    empresa:Empresa = cliente.empresa
    template = loader.get_template('clientes/add_servicio.html')

    if action == ClienteAccionServicios.ADD:
        servicios_allowed = Servicio.objects.filter(empresa=empresa)
        context = {'servicios':servicios_allowed,'action':'add','cliente':cliente}
    elif action == ClienteAccionServicios.REMOVE:
        servicios_allowed = cliente.servicios.all()
        context = {'servicios':servicios_allowed,'action':'remove','cliente':cliente}
    
    if request.method == 'POST':
        servicios_ids = request.POST.getlist('servicios_ids')
        errors = validate_servicios_cliente(request,servicios_ids,servicios_allowed)
        if errors:
            save_log(request, apartado='CLIENTE', accion='ERROR', id_user=request.user.pk, id_cuenta=request.user.cuenta.pk,info='Error al agregar/eliminar servicios a cliente')
            return HttpResponse(template.render(context,request))
        servicios = Servicio.objects.filter(ServicioID__in=servicios_ids)

        if action == ClienteAccionServicios.ADD:
            save_log(request, apartado='CLIENTE', accion='UPDATE', id_user=request.user.pk, id_cuenta=request.user.cuenta.pk,info=f'Servicios agregados al cliente con ID: {cliente.ClienteID}')
            cliente.servicios.add(*servicios)
        elif action == ClienteAccionServicios.REMOVE:
            save_log(request, apartado='CLIENTE', accion='UPDATE', id_user=request.user.pk, id_cuenta=request.user.cuenta.pk,info=f'Servicios eliminados del cliente con ID: {cliente.ClienteID}')
            cliente.servicios.remove(*servicios)
        return redirect('/backoffice/clientes/'+str(cliente.ClienteID))
    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))