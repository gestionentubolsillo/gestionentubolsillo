from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template import loader
from django.http import HttpResponse, HttpRequest
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.contrib import messages
from users.models import can_access_backoffice
from clientes.models import Cliente,user_client,can_view_clientes,can_CRUD_clientes
from django.utils.timezone import now

from clientes.paginators import paginate_cliente_users
from clientes.builders import build_user_client
from clientes.validators import validate_user_client, can_client_access_user_cli, validate_auth_client


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
@require_http_methods(["GET","POST"])
def create_user_client(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    auth_error = validate_auth_client(request,cliente)
    if auth_error:
        return auth_error
    return _create_or_modify_user_cliente(request,cliente)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
@require_http_methods(["GET","POST"])
def edit_user_client(request:HttpRequest,client_id,user_client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    auth_error = validate_auth_client(request,cliente)
    if auth_error:
        return auth_error
    user_cli = user_client.objects.filter(id=user_client_id).first()
    cli_error = can_client_access_user_cli(request,cliente,user_cli)
    if cli_error:
        return redirect('backoffice/clientes/'+str(client_id)+'/users')
    
    return _create_or_modify_user_cliente(request,cliente,user_cli)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
@require_POST
def delete_user_client(request:HttpRequest,client_id,user_client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    auth_error = validate_auth_client(request,cliente)
    if auth_error:
        return auth_error
    user_cli = user_client.objects.filter(id=user_client_id).first()
    cli_error = can_client_access_user_cli(request,cliente,user_cli)
    if cli_error:
        return redirect('backoffice/clientes/'+str(client_id)+'/users')
    user_cli.delete()
    messages.success(request,"El usuario proporcionado al cliente ha sido eliminado con éxito",extra_tags='success')
    return redirect('backoffice/clientes/'+str(client_id)+'/users')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_clientes)
@require_GET
def user_client_details(request:HttpRequest,client_id,user_client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    auth_error = validate_auth_client(request,cliente)
    if auth_error:
        return auth_error
    user_cli = user_client.objects.filter(id=user_client_id).first()
    cli_error = can_client_access_user_cli(request,cliente,user_cli)
    if cli_error:
        return redirect('backoffice/clientes/'+str(client_id)+'/users')
    context = {
        'user_cli':user_cli,
        'action':'view'
    }
    return render(request,'u_cli_form.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_clientes)
@require_GET
def list_user_client(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    auth_error = validate_auth_client(request,cliente)
    if auth_error:
        return auth_error
    context = paginate_cliente_users(request,cliente)
    return render(request,'backoffice/u_cli_list.html',context)

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