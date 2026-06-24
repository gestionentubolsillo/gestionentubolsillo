from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import cli_login_required
from django.template import loader
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from users.models import User, can_access_backoffice
from .models import Cliente,user_client,can_view_clientes,can_CRUD_clientes
from servicios.models import Servicio, can_CRUD_servicios
from django.utils.timezone import now
from empresas.models import Empresa
from enum import Enum

from .filters import filtra_clientes
from .paginators import paginate_clientes, paginate_servicios_de_cliente, paginate_cliente_users
from .builders import build_cliente,build_user_client
from .validators import validate_client, validate_user_client,validate_servicios_cliente, can_client_access_user_cli

# Create your views here.
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
    return _create_or_modify_user_cliente(request,cliente)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
def edit_user_client(request:HttpRequest,client_id,user_client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    user_cli = user_client.objects.filter(id=user_client_id).first()
    auth_error = can_client_access_user_cli(request,cliente,user_cli)
    if auth_error:
        return redirect('backoffice/clientes/'+str(client_id)+'/users')
    
    return _create_or_modify_user_cliente(request,cliente,user_cli)

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
    context = paginate_cliente_users(request,cliente)
    return render(request,'backoffice/u_cli_list.html',context)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
def add_servicios_to_cliente(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(ClienteID=client_id).first()
    return _change_servicios_de_cliente(request,cliente,action=ClienteAccionServicios.ADD)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
def remove_servicios_to_cliente(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(ClienteID=client_id).first()
    return _change_servicios_de_cliente(request,cliente,action=ClienteAccionServicios.REMOVE)

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
    

def _create_or_modify_user_cliente(request:HttpRequest,cliente:Cliente,user_cli:user_client|None=None):
    template = loader.get_template('u_cli_form.html')
    servicios = cliente.servicios.all()
    if user_cli is None:
        context = {'action':'create','servicios':servicios}
    else:
        context = {'action':'edit','servicios':servicios}

    if request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        errors = validate_user_client(request,username,password)
        if errors:
            return HttpResponse(template.render(context,request))
        
        created_at = now()
        servicios_ids = request.POST.getlist('servicios')
        servicios_validos = cliente.servicios.filter(ServicioID__in=servicios_ids)
        build_user_client(data={
            'username':username,
            'password':password,
            'cliente':cliente
        },servicios=servicios_validos,created_at=created_at,user_cli=user_cli)
        return redirect('backoffice/clientes/'+str(cliente.ClienteID)+'/users')


    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))