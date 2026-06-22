from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import cli_login_required
from django.template import loader
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.core.paginator import Paginator
from users.models import User, can_access_backoffice
from .models import Cliente,user_client,can_view_clientes,can_CRUD_clientes
from servicios.models import Servicio, can_CRUD_servicios
from django.utils.timezone import now
from empresas.models import Empresa
from django.db.models.manager import BaseManager
from enum import Enum

from .filters import filtra_clientes
from .paginators import paginate_clientes, paginate_servicios_de_cliente
from .builders import build_cliente
from .validators import validate_client, validate_user_client,validate_servicios_cliente

# Create your views here.
DEFAULT_PAGINATION_USER_CLI = 25
#Por un lado esta la creacion de organizaciones cliente y por otro, los usuarios tipo cliente asignados a la organizacion


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_clientes)
def list_clientes(request:HttpRequest):

    filtros, exclusiones = filtra_clientes(request)
    lista_clientes = Cliente.objects.filter(**filtros).exclude(**exclusiones).order_by('ClienteID')
    context = paginate_clientes(request,lista_clientes)

    return render(request,'clientes/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
def create_client(request:HttpRequest):
    return _create_or_modify_cliente(request)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
def edit_client(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(ClienteID=client_id).first()
    return _create_or_modify_cliente(request,cliente)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_clientes)
def client_details(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(ClienteID=client_id).first()
    if not cliente:
        messages.error(request,"El cliente no existe",extra_tags='error')
        return redirect('/backoffice/clientes')
    context = paginate_servicios_de_cliente(request,cliente)
    return render(request,'clientes/form.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
def delete_client(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    cliente.delete()
    messages.success(request,"El cliente ha sido eliminado con éxito",extra_tags='success')
    return redirect('/backoffice/clientes')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
def create_user_client(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    if request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        #Servicios recibiria una lista de los ids de servicios para añadir las relaciones N:N con respecto al user_client
        servicios_ids = request.POST.getlist('servicios')
        errors = validate_user_client(request,username,password)
        if errors:
            template = loader.get_template('u_cli_form.html')
            context = {}
            return HttpResponse(template.render(context,request))
        
        created_at = now()
        user_cli = user_client()
        user_cli.username = username
        user_cli.set_password(password)
        user_cli.fecha_creacion = created_at
        user_cli.cliente = cliente
        user_cli.save()
        #Añadir relaciones N:N de servicios
        servicios_validos = cliente.servicios.filter(id__in=servicios_ids)
        user_cli.servicios.set(servicios_validos)
        return redirect('backoffice/clientes/'+str(client_id)+'/users')
    
    elif request.method == 'GET':
        servicios = cliente.servicios.all() if cliente else []
        template = loader.get_template('u_cli_form.html')
        context = {
            'servicios':servicios
        }
        return HttpResponse(template.render(context,request))


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

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
def edit_user_client(request:HttpRequest,client_id,user_client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    user_cli = user_client.objects.filter(id=user_client_id).first()
    auth_error = can_client_access_user_cli(request,cliente,user_cli)
    if auth_error:
        return redirect('backoffice/clientes/'+str(client_id)+'/users')
    
    if request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        #Servicios recibiria una lista de los ids de servicios para añadir las relaciones N:N con respecto al user_client
        servicios_ids = request.POST.getlist('servicios')
        errors = validate_user_client(request,username,password)
        if errors:
            template = loader.get_template('u_cli_form.html')
            context = {}
            return HttpResponse(template.render(context,request))
        
        user_cli.username = username
        user_cli.set_password(password)
        user_cli.save()
        #Añadir relaciones N:N de servicios
        servicios_validos = cliente.servicios.filter(id__in=servicios_ids)
        user_cli.servicios.set(servicios_validos)
        return redirect('backoffice/clientes/'+str(client_id)+'/users')

    elif request.method == 'GET':
        servicios = cliente.servicios.all() if cliente else []
        template = loader.get_template('u_cli_form.html')
        context = {
            'servicios':servicios
        }
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
def delete_user_client(request:HttpRequest,client_id,user_client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    user_cli = user_client.objects.filter(id=user_client_id).first()
    auth_error = can_client_access_user_cli(request,cliente,user_cli)
    if auth_error:
        return redirect('backoffice/clientes/'+str(client_id)+'/users')
    user_cli.delete()
    messages.success(request,"El usuario proporcionado al cliente ha sido eliminado con éxito",extra_tags='success')
    return redirect('backoffice/clientes/'+str(client_id)+'/users')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_clientes)
def user_client_details(request:HttpRequest,client_id,user_client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    user_cli = user_client.objects.filter(id=user_client_id).first()
    auth_error = can_client_access_user_cli(request,cliente,user_cli)
    if auth_error:
        return redirect('backoffice/clientes/'+str(client_id)+'/users')
    context = {
        'user_cli':user_cli,
        'action':'view'
    }
    return render(request,'u_cli_form.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_clientes)
def list_user_client(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_USER_CLI
    n_user_clis = request.GET.get('n_us_clis', DEFAULT_PAGINATION_USER_CLI)
    lista_user_clis = user_client.objects.filter(cliente_id = cliente.ClienteID)
    paginacion = Paginator(lista_user_clis,n_user_clis)
    page_obj = paginacion.get_page(n_pagina)

    context = {
        'user_clis':page_obj,
        'page_obj':page_obj,
        'page':n_pagina,
        'n_user_clis':n_user_clis
    }
    return render(request,'backoffice/u_cli_list.html',context)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
def add_servicios_to_cliente(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(ClienteID=client_id).first()
    empresa:Empresa = cliente.empresa
    allowed_services_to_add = Servicio.objects.filter(empresa=empresa)

    if request.method == 'POST':
        servicios_ids = request.POST.getlist('servicios_ids')
        errors = validate_servicios_cliente(request,servicios_ids,allowed_services_to_add)
        if errors:
            template = loader.get_template('clientes/add_servicio.html')
            context = {'servicios':allowed_services_to_add,'action':'add','cliente':cliente}
            return HttpResponse(template.render(context,request))
        servicios = Servicio.objects.filter(ServicioID__in=servicios_ids)
        cliente.servicios.add(*servicios)
        return redirect('/backoffice/clientes/'+str(client_id))
    elif request.method == 'GET':
        template = loader.get_template('clientes/add_servicio.html')
        context = {'servicios':allowed_services_to_add,'action':'add','cliente':cliente}
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
def remove_servicios_to_cliente(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(ClienteID=client_id).first()
    servicios_de_cliente:BaseManager[Servicio] = cliente.servicios.all()
    if request.method == 'POST':
        servicios_ids = request.POST.getlist('servicios_ids')
        errors = validate_servicios_cliente(request,servicios_ids,servicios_de_cliente)
        if errors:
            template = loader.get_template('clientes/add_servicio.html')
            context = {'servicios':servicios_de_cliente,'action':'remove','cliente':cliente}
            return HttpResponse(template.render(context,request))
        servicios = Servicio.objects.filter(ServicioID__in=servicios_ids)
        cliente.servicios.remove(*servicios)
        return redirect('/backoffice/clientes/'+str(client_id))
    elif request.method == 'GET':
        template = loader.get_template('clientes/add_servicio.html')
        context = {'servicios':servicios_de_cliente,'action':'remove','cliente':cliente}
        return HttpResponse(template.render(context,request))


def _create_or_modify_cliente(request:HttpRequest,cliente:Cliente|None = None):
    template = loader.get_template('clientes/form.html')
    user:User = request.user
    empresas = Empresa.objects.filter(usuario_creador_id=user.UserID)

    if cliente is None:
        context = {'action':'create','empresas':empresas}
    else:
        context = {'action':'edit','cliente':cliente,'empresas':empresas}

    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        mail = request.POST.get('mail','')
        contacto = request.POST.get('contacto','')
        direccion = request.POST.get('direccion','')
        provincia = request.POST.get('provincia','')
        municipio = request.POST.get('municipio','')
        telefono = request.POST.get('telefono','')
        empresa_id = request.POST.get('empresa','')
        
        errors = validate_client(request,nombre,provincia,municipio,empresa_id)
        if errors:
            return HttpResponse(template.render(context,request))
        created_at = now()
        empresa = Empresa.objects.filter(EmpresaID=empresa_id).first()
        build_cliente(data={'nombre':nombre,
            'mail':mail,
            'contacto':contacto,
            'direccion':direccion,
            'provincia':provincia,
            'municipio':municipio,
            'telefono':telefono,
            'empresa':empresa},created_at=created_at,cliente=cliente)
        
        return redirect('/backoffice/clientes')
        

    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))
    

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
            return HttpResponse(template.render(context,request))
        servicios = Servicio.objects.filter(ServicioID__in=servicios_ids)

        if action == ClienteAccionServicios.ADD:
            cliente.servicios.add(*servicios)
        elif action == ClienteAccionServicios.REMOVE:
            cliente.servicios.remove(*servicios)
        return redirect('/backoffice/clientes/'+str(cliente.ClienteID))
    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))