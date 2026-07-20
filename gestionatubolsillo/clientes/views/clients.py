from django.shortcuts import render, redirect
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpRequest
from django.views.decorators.http import require_POST, require_GET, require_http_methods

from django.utils.timezone import now
from django.contrib import messages

from clientes.models import Cliente, can_view_clientes, can_CRUD_clientes
from users.models import User, can_access_backoffice
from empresas.models import Empresa

from clientes.filters import filtra_clientes
from clientes.paginators import paginate_clientes, paginate_servicios_de_cliente
from clientes.validators import validate_client, validate_auth_client
from clientes.builders import build_cliente

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_clientes)
@require_GET
def list_clientes(request:HttpRequest):

    filtros, exclusiones = filtra_clientes(request)
    lista_clientes = Cliente.objects.filter(**filtros).exclude(**exclusiones).order_by('ClienteID')
    context = paginate_clientes(request,lista_clientes)

    return render(request,'clientes/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
@require_http_methods(["GET","POST"])
def create_client(request:HttpRequest):
    return _create_or_modify_cliente(request)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
@require_http_methods(["GET","POST"])
def edit_client(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(ClienteID=client_id).first()
    auth_error = validate_auth_client(request,cliente)
    if auth_error:
        return auth_error
    return _create_or_modify_cliente(request,cliente)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_clientes)
@require_GET
def client_details(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(ClienteID=client_id).first()
    auth_error = validate_auth_client(request,cliente)
    if auth_error:
        return auth_error
    context = paginate_servicios_de_cliente(request,cliente)
    return render(request,'clientes/form.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_clientes)
@require_POST
def delete_client(request:HttpRequest,client_id):
    cliente = Cliente.objects.filter(id=client_id).first()
    auth_error = validate_auth_client(request,cliente)
    if auth_error:
        return auth_error
    cliente.delete()
    messages.success(request,"El cliente ha sido eliminado con éxito",extra_tags='success')
    return redirect('/backoffice/clientes')

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
            'empresa':empresa},created_at=created_at,cliente=cliente,cuenta=user.cuenta)
        
        return redirect('/backoffice/clientes')
        

    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))