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

DEFAULT_PAGINATION_SERVICIOS = 25
# Create your views here.

def validate_servicio(request:HttpRequest,nombre,
                      dias_semana,hora_inicio,hora_fin,clientes_ids,empresa_id)->bool:
    errors = False
    empresa = Empresa.objects.filter(id=empresa_id).first()
    are_asigned_clients = Cliente.objects.exists(id__in = clientes_ids)
    if nombre == '':
        messages.error(request,"Debe indicar un nombre al servicio",extra_tags='error')
        errors = True
    if dias_semana and not (hora_inicio or hora_fin):
        messages.error(request,"Debe indicar un horario si ha asignado días",extra_tags='error')
        errors = True
    if not empresa:
        messages.error(request,"Debe indicar la empresa que proporciona el servicio",extra_tags='error')
        errors = True
    if not are_asigned_clients:
        messages.error(request,"Debe asignar clientes que utilizan el servicio",extra_tags='error')
        errors = True
    return errors

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_servicios)
def list_servicios(request:HttpRequest):
    user:User = request.user
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
        'n_servicios':n_servicios
    }

    return render(request,'backoffice/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
def create_servicio(request:HttpRequest):
    if request.method == 'POST':
        created_at = now()
        nombre = request.POST.get('nombre','')
        descripcion = request.POST.get('descripcion','')
        mail = request.POST.get('mail','')
        dias_semana = request.POST.getlist('dias_semana')
        hora_inicio = request.POST.get('hora_inicio','')
        hora_fin = request.POST.get('hora_fin','')
        precio_hora = request.POST.get('precio_hora',0.)
        is_active = request.POST.get('is_active')=='on'
        es_exterior = request.POST.get('es_exterior')=='on'
        requiere_gps = request.POST.get('gps_on')=='on'
        clientes_ids = request.POST.getlist('clientes_ids')
        empresa_id = request.POST.get('empresa_id','')
        errors = validate_servicio(request,nombre,dias_semana,hora_inicio,hora_fin,clientes_ids,empresa_id)
        if errors:
            template = loader.get_template('form.html')
            context = {}
            return HttpResponse(template.render(context,request))
        servicio = Servicio()
        servicio.nombre = nombre
        servicio.descripcion = descripcion
        servicio.dias_semana = dias_semana
        servicio.hora_inicio = hora_inicio
        servicio.hora_fin = hora_fin
        servicio.precio_por_hora = precio_hora
        servicio.is_active = is_active
        servicio.es_exterior = es_exterior
        servicio.empresa
        servicio.mail_de_contacto = mail
        servicio.requiere_gps = requiere_gps
        servicio.fecha_creacion = created_at
        servicio.save()

        #Relacion N:N con el modelo Cliente
        clientes = Cliente.objects.filter(id__in = clientes_ids)
        servicio.clientes.set(clientes)

        return redirect('backoffice/servicios')
    elif request.method == 'GET':
        template = loader.get_template('form.html')
        context = {}
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
def edit_servicio(request:HttpRequest,servicio_id):
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        template = loader.get_template('form.html')
        context = {}
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_servicios)
def servicio_details(request:HttpRequest,servicio_id):
    servicio = Servicio.objects.filter(id=servicio_id).first()
    if not servicio:
        messages.error(request,"El servicio no existe",extra_tags='error')
        return redirect('backoffice/servicios')
    context = {
        'servicio':servicio,
        'action':'view'
    }
    return render(request,'form.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_servicios)
def delete_servicio(request:HttpRequest,servicio_id):
    servicio = Servicio.objects.filter(id=servicio_id).first()
    servicio.delete()
    messages.success(request,"El servicio ha sido eliminado con éxito",extra_tags='success')
    return redirect('backoffice/servicios')