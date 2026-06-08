from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse
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

DEFAULT_PAGINATION_SERVICIOS = 25
DEFAULT_PAGINATION_SERVICIOS_CLIENTES = 25
# Create your views here.

def validate_servicio(request:HttpRequest,nombre,
                      dias_semana,hora_inicio,hora_fin,empresa_id)->bool:
    errors = False
    empresa = Empresa.objects.filter(EmpresaID=empresa_id).first()
    if nombre == '':
        messages.error(request,"Debe indicar un nombre al servicio",extra_tags='error')
        errors = True
    if dias_semana and not (hora_inicio or hora_fin):
        messages.error(request,"Debe indicar un horario si ha asignado días",extra_tags='error')
        errors = True
    if not empresa:
        messages.error(request,"Debe indicar la empresa que proporciona el servicio",extra_tags='error')
        errors = True
    return errors


def validate_clientes_servicio(request:HttpRequest, clientes_ids,allowed_clients_to_add:BaseManager[Cliente])->bool:
    errors = False
    if not clientes_ids:
        messages.error(request, "Debe seleccionar al menos un cliente", extra_tags='error')
        errors = True
    clientes = Cliente.objects.filter(ClienteID__in=clientes_ids)
    if not clientes:
        messages.error(request, "No se ha podido encontrar ningún cliente", extra_tags='error')
        errors = True
    clientes_no_permitidos = clientes.difference(allowed_clients_to_add)
    if clientes_no_permitidos.exists():
        messages.error(request, "No puede añadir clientes no autorizados a este servicio", extra_tags='error')
        errors = True
    return errors

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_servicios)
def list_servicios(request:HttpRequest):
    user:User = request.user
    empresas = Empresa.objects.filter(usuario_creador_id=user.UserID)
    empresa:Empresa = user.empresa
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_SERVICIOS
    n_servicios = request.GET.get('n_servicios', DEFAULT_PAGINATION_SERVICIOS)
    filtro_empresa = request.GET.get('empresa',empresa.EmpresaID)

    lista_servicios = Servicio.objects.filter(empresa_id = filtro_empresa)
    paginacion = Paginator(lista_servicios,n_servicios)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'servicios':page_obj,
        'page_obj':page_obj,
        'page':n_pagina,
        'n_servicios':n_servicios,
        'empresas':empresas
    }

    return render(request,'servicios/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
def create_servicio(request:HttpRequest):
    dias_choices = Servicio._meta.get_field('dias_semana').choices
    user:User = request.user
    empresas = Empresa.objects.filter(usuario_creador_id = user.UserID)
    if request.method == 'POST':
        created_at = now()
        nombre = request.POST.get('nombre','')
        descripcion = request.POST.get('descripcion','')
        mail = request.POST.get('mail','')
        dias_semana = request.POST.getlist('dias_semana')
        hora_inicio = request.POST.get('hora_inicio','')
        hora_fin = request.POST.get('hora_fin','')
        precio_hora = Decimal(request.POST.get('precio_hora',0.))
        is_active = request.POST.get('is_active')=='on'
        es_exterior = bool(int(request.POST.get('es_exterior',1)))
        requiere_gps = request.POST.get('gps_on')=='on'
        empresa_id = request.POST.get('empresa_id','')
        errors = validate_servicio(request,nombre,dias_semana,hora_inicio,hora_fin,empresa_id)
        if errors:
            template = loader.get_template('servicios/form.html')
            context = {'action':'create',
                       'dias_choices':dias_choices,
                       'empresas':empresas
                       }
            return HttpResponse(template.render(context,request))
        empresa = Empresa.objects.filter(EmpresaID=empresa_id).first()
        servicio = Servicio()
        servicio.nombre = nombre
        servicio.descripcion = descripcion
        servicio.dias_semana = dias_semana
        servicio.hora_inicio = hora_inicio
        servicio.hora_fin = hora_fin
        servicio.precio_por_hora = precio_hora
        servicio.is_active = is_active
        servicio.es_exterior = es_exterior
        servicio.empresa = empresa
        servicio.mail_de_contacto = mail
        servicio.requiere_gps = requiere_gps
        servicio.fecha_creacion = created_at
        servicio.save()

        return redirect('/backoffice/servicios')
    elif request.method == 'GET':
        template = loader.get_template('servicios/form.html')
        context = {'action':'create',
                   'dias_choices':dias_choices,
                   'empresas':empresas
                   }
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
def edit_servicio(request:HttpRequest,servicio_id):
    user:User = request.user
    dias_choices = Servicio._meta.get_field('dias_semana').choices
    empresas = Empresa.objects.filter(usuario_creador_id = user.UserID)
    servicio = Servicio.objects.filter(ServicioID=servicio_id).first()
    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        descripcion = request.POST.get('descripcion','')
        mail = request.POST.get('mail','')
        dias_semana = request.POST.getlist('dias_semana')
        hora_inicio = request.POST.get('hora_inicio','')
        hora_fin = request.POST.get('hora_fin','')
        precio_hora = Decimal(request.POST.get('precio_hora',0.))
        is_active = request.POST.get('is_active')=='on'
        es_exterior = bool(int(request.POST.get('es_exterior',1)))
        requiere_gps = request.POST.get('gps_on')=='on'
        empresa_id = request.POST.get('empresa_id','')
        errors = validate_servicio(request,nombre,dias_semana,hora_inicio,hora_fin,empresa_id)
        if errors:
            template = loader.get_template('servicios/form.html')
            context = {
                'action':'edit',
                'dias_choices':dias_choices,
                'empresas':empresas,
                'servicio':servicio
                }
            return HttpResponse(template.render(context,request))
        empresa = Empresa.objects.filter(EmpresaID=empresa_id).first()
        servicio.nombre = nombre
        servicio.descripcion = descripcion
        servicio.dias_semana = dias_semana
        servicio.hora_inicio = hora_inicio
        servicio.hora_fin = hora_fin
        servicio.precio_por_hora = precio_hora
        servicio.is_active = is_active
        servicio.es_exterior = es_exterior
        servicio.empresa = empresa
        servicio.mail_de_contacto = mail
        servicio.requiere_gps = requiere_gps
        servicio.save()

        return redirect('/backoffice/servicios')
    elif request.method == 'GET':
        template = loader.get_template('servicios/form.html')
        context = {
            'action':'edit',
            'dias_choices':dias_choices,
            'empresas':empresas,
            'servicio':servicio
            }
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_servicios)
def servicio_details(request:HttpRequest,servicio_id):
    servicio = Servicio.objects.filter(ServicioID=servicio_id).first()
    dias_choices = Servicio._meta.get_field('dias_semana').choices
    if not servicio:
        messages.error(request,"El servicio no existe",extra_tags='error')
        return redirect('/backoffice/servicios')
    
    #Paginacion de clientes
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_SERVICIOS_CLIENTES
    n_clientes = request.GET.get('n_clientes', DEFAULT_PAGINATION_SERVICIOS_CLIENTES)
    lista_clientes = servicio.clientes.all()
    paginacion = Paginator(lista_clientes,n_clientes)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'servicio':servicio,
        'dias_choices':dias_choices,
        'action':'view',
        'clientes':page_obj,
        'page_obj':page_obj,
        'page':n_pagina,
        'n_clientes':n_clientes,
    }
    return render(request,'servicios/form.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
def delete_servicio(request:HttpRequest,servicio_id):
    servicio = Servicio.objects.filter(ServicioID=servicio_id).first()
    servicio.delete()
    messages.success(request,"El servicio ha sido eliminado con éxito",extra_tags='success')
    return redirect('/backoffice/servicios')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
def add_clientes_to_servicio(request:HttpRequest,servicio_id):
    servicio = Servicio.objects.filter(ServicioID=servicio_id).first()
    empresa:Empresa = servicio.empresa
    allowed_clients_to_add = Cliente.objects.filter(empresa=empresa)
    if request.method == 'POST':
        clientes_ids = request.POST.getlist('clientes_ids')
        
        errors = validate_clientes_servicio(request,clientes_ids, allowed_clients_to_add)
        if errors:
            template = loader.get_template('servicios/add_clients.html')
            context = {'clientes':allowed_clients_to_add, 'action':'add', 'servicio':servicio}
            return HttpResponse(template.render(context,request))
        
        clientes = Cliente.objects.filter(ClienteID__in=clientes_ids)
        servicio.clientes.add(*clientes)
        return redirect('/backoffice/servicios/'+str(servicio_id))
    elif request.method == 'GET':
        template = loader.get_template('servicios/add_clients.html')
        context = {'clientes':allowed_clients_to_add, 'action':'add'}
        return HttpResponse(template.render(context,request))
    
def remove_clientes_to_servicio(request:HttpRequest,servicio_id):
    servicio = Servicio.objects.filter(ServicioID=servicio_id).first()
    clientes_de_servicio:BaseManager[Cliente] = servicio.clientes.all()
    if request.method == 'POST':
        clientes_ids = request.POST.getlist('clientes_ids')
        
        errors = validate_clientes_servicio(request,clientes_ids, clientes_de_servicio)
        if errors:
            template = loader.get_template('servicios/add_clients.html')
            context = {'clientes':clientes_de_servicio, 'action':'remove'}
            return HttpResponse(template.render(context,request))
        
        clientes = Cliente.objects.filter(ClienteID__in=clientes_ids)
        servicio.clientes.remove(*clientes)
        return redirect('/backoffice/servicios/'+str(servicio_id))
    elif request.method == 'GET':
        template = loader.get_template('servicios/add_clients.html')
        context = {'clientes':clientes_de_servicio, 'action':'remove','servicio':servicio}
        return HttpResponse(template.render(context,request))
