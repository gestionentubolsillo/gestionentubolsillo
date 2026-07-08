from datetime import datetime

from django.shortcuts import render, redirect
from django.http import HttpRequest,HttpResponse, JsonResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.http import require_POST
from django.template import loader
from django.core.paginator import Paginator
from users.models import User, can_access_backoffice
from django.contrib import messages
from django.db.models import Count, Sum, Q, F, ExpressionWrapper, DurationField, FloatField, Value
from django.db.models.functions import Extract, Coalesce, Round, Cast
#Mucha info sale mas rentable importarlo todo
from .models import *
from empresas.models import Empresa
from clientes.models import Cliente
from servicios.models import Servicio
from centrales.models import Central

from .paginators import paginate_informes, paginate_informes_trabajo_resumen
from .validators import validate_parte_trabajo, validate_linea_parte_trabajo, validate_parte_incidencia, validate_parte_acuda
from .builders import build_parte_trabajo, build_linea_parte_trabajo, build_parte_incidencia, build_parte_acuda
from .filters import filtra_partes_trabajo, filtra_partes_incidencia, filtra_partes_inspeccion, filtra_informes_acuda
# Create your views here.
DEFAULT_PAGINATION_PARTES = 25
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
def dashboard_informes(request:HttpRequest):
    #Vista que lista los diferentes enlaces para consulta de los diferentes tipos de informe
    context = {}
    return render(request,'informes/general.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_trabajo)
def list_partes_trabajo(request:HttpRequest):
    filtros, exclusiones, related_fields = filtra_partes_trabajo(request)
    partes = Parte_Trabajo.objects.select_related(*related_fields).filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'informes/trabajo/list.html',context)
    


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_incidencia)
def list_partes_incidencia(request:HttpRequest):
    filtros, exclusiones = filtra_partes_incidencia(request)
    partes = Parte_Incidencia.objects.filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'list_incidencia.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_inspeccion)
def list_partes_inspeccion(request:HttpRequest):
    filtros, exclusiones = filtra_partes_inspeccion(request)
    partes = Parte_Inspeccion.objects.filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'list_inspeccion.html',context)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_acuda)
def list_inf_acuda(request:HttpRequest):
    filtros, exclusiones = filtra_informes_acuda(request)
    partes = Informe_Acuda.objects.filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'list_acuda.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_parte_trabajo)
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
def cerrar_parte_trabajo(request:HttpRequest,parte_id):
    parte = Parte_Trabajo.objects.filter(ParteTrabajoID=parte_id).first()
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
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_parte_incidencia)
def create_parte_incidencia(request:HttpRequest):
    user : User = request.user
    template = loader.get_template('informes/incidencia/form.html')
    allowed_users = User.objects.filter(cuenta=user.cuenta, is_active=True)
    allowed_clientes = Cliente.objects.filter(cuenta=user.cuenta)
    context = {'usuarios':allowed_users,'clientes':allowed_clientes}
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        usuario_id = request.POST.get('usuario_id')
        observaciones = request.POST.get('observaciones','')
        fecha_registrada = request.POST.get('fecha_registrada',None)
        errors = validate_parte_incidencia(request,cliente_id,usuario_id,observaciones)
        if errors:
            return HttpResponse(template.render(context,request))
        created_at = now()
        fecha = datetime.strptime(fecha_registrada, '%Y-%m-%dT%H:%M') if fecha_registrada else None

        incidencia = build_parte_incidencia(data={
            'general':{
                'usuario_asignado':User.objects.get(UserID=usuario_id),
                'cliente':Cliente.objects.get(ClienteID=cliente_id),
                'empresa': User.objects.get(UserID=usuario_id).empresa
            },
            'fecha_hora_incidencia':fecha,
            'texto_incidencia':observaciones
        },user=user,created_at=created_at)

        return redirect('/backoffice/partes_incidencia')
    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))



#Para la inspeccion el inspector que crea el parte no necesita tener acceso al backoffice
"""
@DEPRECATED
Este método de momento no se trabajará
"""
@login_required
@user_passes_test(can_CRUD_parte_inspeccion)
def create_parte_inspeccion(request:HttpRequest):
    user:User = request.user
    template = loader.get_template('informes/inspeccion/form.html')
    allowed_users = User.objects.filter(cuenta=user.cuenta, is_active=True)
    allowed_clientes = Cliente.objects.filter(cuenta=user.cuenta)
    context = {'usuarios':allowed_users,'clientes':allowed_clientes}
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_CRUD_acuda)
def create_inf_acuda(request:HttpRequest):
    user:User = request.user
    template = loader.get_template('informes/acuda/form.html')
    allowed_users = User.objects.filter(cuenta=user.cuenta, is_active=True)
    allowed_clientes = Cliente.objects.filter(cuenta=user.cuenta)
    context = {'usuarios':allowed_users,'clientes':allowed_clientes}
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        usuario_id = request.POST.get('usuario_id')
        central_id = request.POST.get('central_id')
        descripcion = request.POST.get('descripcion','')
        errors = validate_parte_acuda(request,cliente_id,usuario_id,central_id,descripcion)
        if errors:
            return HttpResponse(template.render(context,request))
        created_at = now()
        parte = build_parte_acuda(data={
            'general':{
                'usuario_asignado':User.objects.get(UserID=usuario_id),
                'cliente':Cliente.objects.get(ClienteID=cliente_id),
                'empresa':User.objects.get(UserID=usuario_id).empresa
            },
            'central':Central.objects.get(CentralID=central_id),
            'descripcion':descripcion
        },user=user,created_at=created_at)
        return redirect('/backoffice/informes_acuda')
    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_parte_trabajo)
def add_actividad_to_parte_trabajo(request:HttpRequest,p_trabajo_id):
    template = loader.get_template('informes/trabajo/form.html')
    parte = Parte_Trabajo.objects.filter(ParteTrabajoID=p_trabajo_id).first()
    if not parte:
        messages.error(request, 'No se encontró el parte de trabajo solicitado.', extra_tags='error')
        return redirect('/backoffice/partes_trabajo')

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
def view_parte_trabajo(request:HttpRequest, parte_id):
    parte = Parte_Trabajo.objects.filter(ParteTrabajoID=parte_id).select_related(
        'usuario_creador', 'usuario_asignado', 'cliente', 'empresa', 'servicio'
    ).first()

    if not parte:
        messages.error(request, 'No se encontró el parte de trabajo solicitado.', extra_tags='error')
        return redirect('/backoffice/partes_trabajo')

    context = {'parte': parte, 'lineas': parte.lineas_parte_trabajo.all()}
    return render(request, 'informes/trabajo/pdfview.html', context)

def view_parte_incidencia(request:HttpRequest):
    context = {}
    return render(request,'informes/incidencia/pdfview.html',context)

def view_parte_acuda(request:HttpRequest):
    context = {}
    return render(request,'informes/acuda/pdfview.html',context)

 
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
def list_informes_informe_trabajo(request:HttpRequest):
    filtros, exclusiones, related_fields = filtra_partes_trabajo(request)
    partes = Parte_Trabajo.objects.select_related(*related_fields).filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'informes/trabajo/list_informes.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
def list_informes_informe_trabajo_horas_cliente(request:HttpRequest):
    filtros, exclusiones, related_fields = filtra_partes_trabajo(request)
    partes = Parte_Trabajo.objects.select_related(*related_fields).filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'informes/trabajo/list_horas_cliente.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
def list_informes_informe_trabajo_horas_tecnico(request:HttpRequest):
    filtros, exclusiones,related_fields = filtra_partes_trabajo(request)
    partes = Parte_Trabajo.objects.select_related(*related_fields).filter(**filtros).exclude(**exclusiones).annotate(
        duracion=ExpressionWrapper(
            F('fecha_finalizacion') - F('fecha_creacion'),
            output_field=DurationField()
        )
    ).annotate(
        horas_decimal=ExpressionWrapper(
            Extract('duracion', 'epoch') / 3600.0,
            output_field=FloatField()
        )
    ).annotate(
        precio_servicio=ExpressionWrapper(
                Round(
                    Cast(Coalesce(F('horas_decimal'), Value(0.0)), FloatField()) * Cast(F('servicio__precio_por_hora'), FloatField()),
                    2
                ),
                output_field=FloatField()
            ),
            precio_usuario=ExpressionWrapper(
                Round(
                    Cast(Coalesce(F('horas_decimal'), Value(0.0)), FloatField()) * Cast(F('usuario_asignado__precio_hora'), FloatField()),
                    2
                ),
                output_field=FloatField()
            ),
    ).annotate(
        diferencia=ExpressionWrapper(
            F('precio_servicio')-F('precio_usuario'),
            output_field=FloatField()
        )
    ).order_by('-fecha_creacion')

    resumen_totales = partes.aggregate(
        total_horas_decimal=Coalesce(Sum('horas_decimal'),Value(0.0)),
        total_servicio=Coalesce(Sum('precio_servicio'),Value(0.0)),
        total_usuario=Coalesce(Sum('precio_usuario'),Value(0.0))
    )
    total_horas = int(resumen_totales.get('total_horas_decimal'))
    total_minutos = round((resumen_totales.get('total_horas_decimal')-total_horas)*60)
    total_servicio = round(resumen_totales.get('total_servicio'),2)
    total_usuario = round(resumen_totales.get('total_usuario'),2)
    context = paginate_informes(request,partes)
    context.update({
        'total_horas':total_horas,
        'total_minutos':total_minutos,
        'total_servicio':total_servicio,
        'total_usuario':total_usuario,
        'diferencia': round(total_servicio-total_usuario,2)
    })
    return render(request,'informes/trabajo/list_horas_tecnico.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
def list_informes_informe_trabajo_resumen(request:HttpRequest):
    #No se filtran partes, sino usuarios asignados a los partes para mostrar total de partes asociados al usuario y horas totales de los partes
    filtros, exclusiones, _ = filtra_partes_trabajo(request)
    partes = Parte_Trabajo.objects.filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    #Total horas --> Calcula diferencia entre inicio y fin de cada uno y lo va sumando
    usuarios_asignados = User.objects.filter(parte_trabajo_asignados__in=partes).distinct().annotate(
        num_partes=Count('parte_trabajo_asignados', distinct=True, 
            filter=Q(parte_trabajo_asignados__in=partes)
        )
    ).annotate(
            total_horas=Sum(ExpressionWrapper(F('parte_trabajo_asignados__fecha_finalizacion')-F('parte_trabajo_asignados__fecha_creacion'), 
                output_field=models.DurationField()),
                filter=Q(parte_trabajo_asignados__in=partes)
        )
    ).order_by('UserID')
    context = paginate_informes_trabajo_resumen(request,usuarios_asignados)
    return render(request,'informes/trabajo/list_resumen.html',context)


def list_informes_informe_acuda_cliente(request:HttpRequest):
    filtros, exclusiones = filtra_informes_acuda(request)
    partes = Informe_Acuda.objects.filter(**filtros).exclude(**exclusiones).order_by(-'fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'',context)

def list_informes_informe_acuda_tecnico(request:HttpRequest):
    filtros, exclusiones = filtra_informes_acuda(request)
    partes = Informe_Acuda.objects.filter(**filtros).exclude(**exclusiones).order_by(-'fecha_creacion')
    pass

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
def get_servicios_por_cliente(request:HttpRequest,cliente_id):
    #Vista que devuelve los servicios asociados a un cliente, para ser usados en un select de un formulario
    servicios = Servicio.objects.filter(clientes__ClienteID = cliente_id).values('ServicioID','nombre').distinct()
    return JsonResponse(list(servicios),safe=False)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_parte_trabajo)
def get_servicios_por_cliente_y_usuario(request:HttpRequest,cliente_id,usuario_id):
    #Vista que devuelve los servicios asociados a un cliente y a un usuario, para ser usados en un select de formulario creacion de parte de trabajo
    servicios = Servicio.objects.filter(clientes__ClienteID = cliente_id, users__UserID = usuario_id).values('ServicioID','nombre').distinct()
    return JsonResponse(list(servicios),safe=False)