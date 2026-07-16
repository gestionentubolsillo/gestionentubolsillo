from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.utils.timezone import now
from django.contrib import messages
from django.core.paginator import Paginator
from users.models import can_access_backoffice, User
from empresas.models import Empresa
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template import loader
from .models import Servicio, can_view_servicios, can_CRUD_servicios
from clientes.models import Cliente
from decimal import Decimal
from django.db.models.manager import BaseManager

from .filters import filtra_servicios
from .paginators import paginate_servicios, paginate_clientes_de_servicio
from .validators import validate_servicio, validate_clientes_servicio,validate_auth_servicio
from .builders import build_Servicio
from enum import Enum

# Create your views here.


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_servicios)
@require_GET
def list_servicios(request:HttpRequest):

    filtros, exclusiones = filtra_servicios(request)
    lista_servicios = Servicio.objects.filter(**filtros).exclude(**exclusiones).order_by('ServicioID')
    context = paginate_servicios(request,lista_servicios)

    return render(request,'servicios/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
@require_http_methods(["GET","POST"])
def create_servicio(request:HttpRequest):
    return _create_or_update_servicio(request=request)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
@require_http_methods(["GET","POST"])
def edit_servicio(request:HttpRequest,servicio_id):
    servicio = Servicio.objects.filter(ServicioID=servicio_id).first()

    auth_error = validate_auth_servicio(request,servicio)
    if auth_error:
        return auth_error

    return _create_or_update_servicio(request=request,servicio=servicio)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_servicios)
@require_GET
def servicio_details(request:HttpRequest,servicio_id):
    servicio = Servicio.objects.filter(ServicioID=servicio_id).first()

    auth_error = validate_auth_servicio(request,servicio)
    if auth_error:
        return auth_error
    
    context = paginate_clientes_de_servicio(request=request,servicio=servicio)
    return render(request,'servicios/form.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
@require_POST
def delete_servicio(request:HttpRequest,servicio_id):
    servicio = Servicio.objects.filter(ServicioID=servicio_id).first()

    auth_error = validate_auth_servicio(request,servicio)
    if auth_error:
        return auth_error
    
    servicio.delete()
    messages.success(request,"El servicio ha sido eliminado con éxito",extra_tags='success')
    return redirect('/backoffice/servicios')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
@require_http_methods(["GET","POST"])
def add_clientes_to_servicio(request:HttpRequest,servicio_id):
    servicio = Servicio.objects.filter(ServicioID=servicio_id).first()

    auth_error = validate_auth_servicio(request,servicio)
    if auth_error:
        return auth_error
    
    return _change_clientes_Servicio(request=request,servicio=servicio,action=ServicioAccionClientes.ADD)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
@require_http_methods(["GET","POST"])
def remove_clientes_to_servicio(request:HttpRequest,servicio_id):
    servicio = Servicio.objects.filter(ServicioID=servicio_id).first()

    auth_error = validate_auth_servicio(request,servicio)
    if auth_error:
        return auth_error
    
    return _change_clientes_Servicio(request=request,servicio=servicio,action=ServicioAccionClientes.REMOVE)



class ServicioAccionClientes(Enum):
    ADD = 'add',
    REMOVE = 'remove'

def _change_clientes_Servicio(request:HttpRequest,servicio:Servicio,action:ServicioAccionClientes):

    empresa:Empresa = servicio.empresa
    template = loader.get_template('servicios/add_clients.html')

    if action == ServicioAccionClientes.ADD:
        clientes_allowed = Cliente.objects.filter(empresa=empresa)
        context = {'clientes':clientes_allowed, 'action':'add', 'servicio':servicio}
    elif action == ServicioAccionClientes.REMOVE:
        clientes_allowed :BaseManager[Cliente] = servicio.clientes.all()
        context = {'clientes':clientes_allowed, 'action':'remove','servicio':servicio}

    if request.method == 'POST':
        clientes_ids = request.POST.getlist('clientes_ids')
        
        errors = validate_clientes_servicio(request,clientes_ids, clientes_allowed)
        if errors:
            return HttpResponse(template.render(context,request))
        
        clientes = Cliente.objects.filter(ClienteID__in=clientes_ids)

        if action == ServicioAccionClientes.ADD:
            servicio.clientes.add(*clientes)
        elif action == ServicioAccionClientes.REMOVE:
            servicio.clientes.remove(*clientes)

        return redirect('/backoffice/servicios/'+str(servicio.ServicioID))
    elif request.method == 'GET':

        return HttpResponse(template.render(context,request))


def _create_or_update_servicio(request:HttpRequest,servicio:Servicio | None = None):
    user:User = request.user
    dias_choices = Servicio._meta.get_field('dias_semana').choices
    empresas = Empresa.objects.filter(usuario_creador_id = user.UserID)
    template = loader.get_template('servicios/form.html')
    if servicio is None:
        context = {'action':'create','dias_choices':dias_choices,'empresas':empresas}
    else:
        context = {'action':'edit','dias_choices':dias_choices,'empresas':empresas,'servicio':servicio}
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        descripcion = request.POST.get('descripcion','')
        mail = request.POST.get('mail','')
        dias_semana = request.POST.getlist('dias_semana')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        precio_hora = Decimal(request.POST.get('precio_hora',0.))
        is_active = request.POST.get('is_active')=='on'
        es_exterior = bool(int(request.POST.get('es_exterior',1)))
        requiere_gps = request.POST.get('gps_on')=='on'
        empresa_id = request.POST.get('empresa_id','')
        errors = validate_servicio(request,nombre,dias_semana,hora_inicio,hora_fin,empresa_id)

        if errors:
            return HttpResponse(template.render(context,request))
        
        created_at = now()
        empresa = Empresa.objects.filter(EmpresaID=empresa_id).first()
        build_Servicio(data={
            'nombre':nombre,
            'descripcion':descripcion,
            'dias_semana':dias_semana,
            'hora_inicio':hora_inicio,
            'hora_fin':hora_fin,
            'precio_hora':precio_hora,
            'empresa':empresa,
            'is_active':is_active,
            'is_exterior':es_exterior,
            'mail':mail,
            'need_gps':requiere_gps
        },servicio=servicio,created_at=created_at,user=user)

        return redirect('/backoffice/servicios')
    elif request.method == 'GET':
        
        return HttpResponse(template.render(context,request))

    