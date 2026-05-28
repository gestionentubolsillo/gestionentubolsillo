from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import cli_login_required
from django.template import loader
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.core.paginator import Paginator
from users.models import User, can_access_backoffice
from .models import Cliente,user_client,can_view_clientes,can_CRUD_clientes
from django.utils.timezone import now
from empresas.models import Empresa

# Create your views here.
DEFAULT_PAGINATION_CLIENTS = 25
MIN_CHARS_PASSWORD = 8
DEFAULT_PAGINATION_USER_CLI = 25
#Por un lado esta la creacion de organizaciones cliente y por otro, los usuarios tipo cliente asignados a la organizacion

def validate_client(request:HttpRequest,nombre,provincia,municipio,empresa_id)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe proporcionarle un nombre al cliente", extra_tags='error')
        errors = True
    if provincia == '' or municipio == '':
        messages.error(request,"Debe indicar provincia y municipio al que pertenece",extra_tags='error')
        errors = True
    empresa = Empresa.objects.filter(id=empresa_id).first()
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

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_clientes)
def list_clientes(request:HttpRequest):
    user:User = request.user
    empresa:Empresa = user.empresa
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_CLIENTS
    n_clientes = request.GET.get('n_clients', DEFAULT_PAGINATION_CLIENTS)
    filtro_empresa = request.GET.get('empresa',empresa.EmpresaID)

    lista_clientes = Cliente.objects.filter(empresa_id = filtro_empresa)

    paginacion = Paginator(lista_clientes,n_clientes)
    page_obj = paginacion.get_page(n_pagina)

    context = {
        'clientes':page_obj,
        'page_obj':page_obj,
        'page':n_pagina,
        'n_clients':n_clientes
    }

    return render(request,'backoffice/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
def create_client(request:HttpRequest):
    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        mail = request.POST.get('mail','')
        contacto = request.POST.get('contacto','')
        direccion = request.POST.get('direccion','')
        provincia = request.POST.get('provincia','')
        municipio = request.POST.get('municipio','')
        telefono = request.POST.get('telefono','')
        empresa_id = request.POST.get('empresa','')
        created_at = now()
        errors = validate_client(request,nombre,provincia,municipio,empresa_id)

        if errors:
            template = loader.get_template('form.html')
            context = {}
            return HttpResponse(template.render(context,request))

        empresa = Empresa.objects.filter(id=empresa_id).first()
        cliente = Cliente()
        cliente.nombre = nombre
        cliente.email = mail
        cliente.persona_contacto = contacto
        cliente.direccion = direccion
        cliente.provincia = provincia
        cliente.municipio = municipio
        cliente.telefono = telefono
        cliente.empresa = empresa
        cliente.fecha_creacion = created_at
        cliente.save()
        return redirect('backoffice/clientes')

    elif request.method == 'GET':
        template = loader.get_template('form.html')
        context = {}
        return HttpResponse(template.render(context,request))


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
def edit_client(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
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
            return redirect('backoffice/clientes/edit/'+str(client_id))

        empresa = Empresa.objects.filter(id=empresa_id).first()
        cliente.nombre = nombre
        cliente.email = mail
        cliente.persona_contacto = contacto
        cliente.direccion = direccion
        cliente.provincia = provincia
        cliente.municipio = municipio
        cliente.telefono = telefono
        cliente.empresa = empresa
        cliente.save()
        return redirect('backoffice/clientes/'+str(client_id))
    
    elif request.method == 'GET':
        template = loader.get_template('form.html')
        context = {}
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_clientes)
def client_details(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    if not cliente:
        messages.error(request,"El cliente no existe",extra_tags='error')
        return redirect('backoffice/clientes')
    context = {
        'cliente':cliente,
        'action':'view'
    }
    return render(request,'form.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
def delete_client(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    cliente.delete()
    messages.success(request,"El cliente ha sido eliminado con éxito",extra_tags='success')
    return redirect('backoffice/clientes')

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
