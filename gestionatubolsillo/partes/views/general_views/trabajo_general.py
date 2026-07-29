from django.http import HttpRequest
from django.shortcuts import render

from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.http import require_GET

from django.db.models import Count, Sum, Q, F, ExpressionWrapper, DurationField, FloatField, Value
from django.db.models.functions import Extract, Coalesce, Round, Cast

from users.models import User,can_access_backoffice
from partes.models import Parte_Trabajo,can_view_informes
from django.db import models

from partes.filters import filtra_partes_trabajo
from partes.paginators import paginate_informes,paginate_informes_trabajo_resumen


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
@require_GET
def list_informes_informe_trabajo(request:HttpRequest):
    filtros, exclusiones, related_fields = filtra_partes_trabajo(request)
    partes = Parte_Trabajo.objects.select_related(*related_fields).filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'informes/trabajo/list_informes.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
@require_GET
def list_informes_informe_trabajo_horas_cliente(request:HttpRequest):
    filtros, exclusiones, related_fields = filtra_partes_trabajo(request)
    partes = Parte_Trabajo.objects.select_related(*related_fields).filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'informes/trabajo/list_horas_cliente.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_informes)
@require_GET
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
@require_GET
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