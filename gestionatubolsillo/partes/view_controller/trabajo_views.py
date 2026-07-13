from django.http import HttpRequest,HttpResponse
from django.template import loader
from django.contrib import messages

from django.utils.timezone import now
from django.contrib.auth.decorators import login_required,user_passes_test
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST,require_GET,require_http_methods
from users.models import User, can_access_backoffice

from  partes.models import Parte_Trabajo, Linea_Parte_Trabajo, can_view_parte_trabajo, can_CRUD_parte_trabajo
from partes.paginators import paginate_informes
from partes.filters import filtra_partes_trabajo
from partes.builders import build_parte_trabajo, build_linea_parte_trabajo
from partes.validators import validate_parte_trabajo,validate_linea_parte_trabajo, validate_auth_parte

from clientes.models import Cliente
from servicios.models import Servicio
from datetime import datetime

ERROR_NOT_FOUND_REDIRECT = '/backoffice/partes_trabajo'

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_trabajo)
@require_GET
def list_partes_trabajo(request:HttpRequest):
    filtros, exclusiones, related_fields = filtra_partes_trabajo(request)
    partes = Parte_Trabajo.objects.select_related(*related_fields).filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'informes/trabajo/list.html',context)



@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_parte_trabajo)
@require_http_methods(["GET","POST"])
def create_parte_trabajo(request:HttpRequest):
    user : User = request.user
    template = loader.get_template('informes/trabajo/form.html')
    allowed_users = User.objects.filter(cuenta=user.cuenta, is_active=True)
    allowed_clientes = Cliente.objects.filter(cuenta=user.cuenta)
    context = {'usuarios': allowed_users, 'clientes': allowed_clientes, 'action':'create'}
    if request.method == 'POST':
        #Aquí se procesaría el formulario de creación de parte de trabajo
        cliente_id = request.POST.get('cliente_id')
        servicio_id = request.POST.get('servicio_id')
        usuario_id = request.POST.get('usuario_id')
        observaciones = request.POST.get('observaciones','')
        fecha_registrada = request.POST.get('fecha_registrada',None)

        errors = validate_parte_trabajo(request, cliente_id, servicio_id, usuario_id)
        if errors:
            return HttpResponse(template.render(context,request))
        created_at = now()
        fecha = datetime.strptime(fecha_registrada, '%Y-%m-%dT%H:%M') if fecha_registrada else None
        build_parte_trabajo(data={
            'general':{
                'usuario_asignado': User.objects.get(UserID=usuario_id),
                'cliente': Cliente.objects.get(ClienteID=cliente_id),
                'empresa': User.objects.get(UserID=usuario_id).empresa
            },
            'servicio': Servicio.objects.get(ServicioID=servicio_id),
            'observaciones': observaciones
        }, user=user,created_at=created_at, fecha_inicio_registrada=fecha)

        return redirect('/backoffice/partes_trabajo')

    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))
    

@login_required
@require_POST
@user_passes_test(can_CRUD_parte_trabajo)
@require_POST
def cerrar_parte_trabajo(request:HttpRequest,parte_id):
    parte = Parte_Trabajo.objects.filter(ParteTrabajoID=parte_id).first()
    auth_error = validate_auth_parte(request,parte,ERROR_NOT_FOUND_REDIRECT)
    if auth_error:
        return auth_error
    ended_at = now()
    fecha_fin_registrada = request.POST.get('fecha_fin')
    if not fecha_fin_registrada:
        fecha_fin_registrada = ended_at
    parte.fecha_finalizacion = ended_at
    parte.fecha_finalizacion_registrada = fecha_fin_registrada
    parte.save()

    linea_fin = Linea_Parte_Trabajo()
    linea_fin.actividad = 'Finalización'
    linea_fin.fecha_creacion = ended_at
    linea_fin.fecha_registrada = fecha_fin_registrada
    linea_fin.parte_trabajo = parte
    linea_fin.save()
    return redirect(f'/backoffice/partes/{parte_id}')

@login_required
@require_POST
@user_passes_test(can_CRUD_parte_trabajo)
@require_POST
def relevar_usuario_parte_trabajo(request:HttpRequest,parte_id):
    parte = Parte_Trabajo.objects.filter(ParteTrabajoID=parte_id).first()
    auth_error = validate_auth_parte(request,parte,ERROR_NOT_FOUND_REDIRECT)
    if auth_error:
        return auth_error

    usuario_relevo_id = request.POST.get('usuario_id')
    fecha_relevo = request.POST.get('fecha_hora_relevo') or request.POST.get('fecha_relevo')

    usuario_relevo = None
    if usuario_relevo_id:
        usuario_relevo = User.objects.filter(UserID=usuario_relevo_id).first()

    relevo_at = datetime.strptime(fecha_relevo, '%Y-%m-%dT%H:%M') if fecha_relevo else now()
    usuario_saliente : User = parte.usuario_asignado

    parte.usuario_relevo = usuario_relevo
    parte.fecha_hora_relevo = relevo_at
    parte.fecha_hora_relevo_registrada = relevo_at
    if usuario_relevo:
        parte.usuario_asignado = usuario_relevo
    parte.save()

    if usuario_saliente and usuario_relevo:
        extra_info = f'{usuario_saliente.username} releva al {usuario_relevo.username}'
    elif usuario_relevo:
        extra_info = f'Relevo asignado a {usuario_relevo.username}'
    else:
        extra_info = 'Relevo sin usuario asociado'

    Linea_Parte_Trabajo.objects.create(
        actividad='Relevo',
        extra_info=extra_info,
        fecha_creacion=relevo_at,
        fecha_registrada=relevo_at,
        parte_trabajo=parte,
    )

    return redirect(f'/backoffice/partes/{parte_id}')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_parte_trabajo)
@require_http_methods(["GET","POST"])
def add_actividad_to_parte_trabajo(request:HttpRequest,p_trabajo_id):
    template = loader.get_template('informes/trabajo/form.html')
    parte = Parte_Trabajo.objects.filter(ParteTrabajoID=p_trabajo_id).first()
    auth_error = validate_auth_parte(request,parte,ERROR_NOT_FOUND_REDIRECT)
    if auth_error:
        return auth_error

    lineas = parte.lineas_parte_trabajo.all()
    choices = Linea_Parte_Trabajo._meta.get_field('actividad').choices
    context = {'parte':parte,'lineas':lineas, 'action':'view','choices':choices}
    if request.method == 'POST':
        actividad = request.POST.get('actividad')
        fecha_registrada = request.POST.get('fecha')
        extra_info = request.POST.get('extra')
        errors = validate_linea_parte_trabajo(request,actividad)
        if errors:
            return HttpResponse(template.render(context,request))
        created_at = now()
        fecha = datetime.strptime(fecha_registrada, '%Y-%m-%dT%H:%M') if fecha_registrada else None

        build_linea_parte_trabajo(data={
            'actividad':actividad,
            'extra_info':extra_info,
            'fecha_registrada':fecha,
            'parte_trabajo':parte
        },created_at=created_at)
        return redirect(f'/backoffice/partes_trabajo/{p_trabajo_id}/actividades')

    if request.method == 'GET':
        return HttpResponse(template.render(context,request))

#Necesario indagar más en estas caracteristicas
@require_GET
def view_parte_trabajo(request:HttpRequest, parte_id):
    parte = Parte_Trabajo.objects.filter(ParteTrabajoID=parte_id).select_related(
        'usuario_creador', 'usuario_asignado', 'cliente', 'empresa', 'servicio'
    ).first()

    auth_error = validate_auth_parte(request,parte,ERROR_NOT_FOUND_REDIRECT)
    if auth_error:
        return auth_error

    context = {'parte': parte, 'lineas': parte.lineas_parte_trabajo.all()}
    return render(request, 'informes/trabajo/pdfview.html', context)