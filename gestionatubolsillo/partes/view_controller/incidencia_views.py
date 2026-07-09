from django.http import HttpRequest,HttpResponse
from django.template import loader
from django.contrib import messages

from django.utils.timezone import now
from django.contrib.auth.decorators import login_required,user_passes_test
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from users.models import User, can_access_backoffice

from partes.models import Parte_Incidencia,can_view_parte_incidencia,can_CRUD_parte_incidencia
from partes.filters import filtra_partes_incidencia
from partes.paginators import paginate_informes
from partes.builders import build_parte_incidencia
from partes.validators import validate_parte_incidencia

from datetime import datetime
from clientes.models import Cliente


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_parte_incidencia)
def list_partes_incidencia(request:HttpRequest):
    filtros, exclusiones = filtra_partes_incidencia(request)
    partes = Parte_Incidencia.objects.filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'informes/incidencia/list.html',context)

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

        build_parte_incidencia(data={
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
    
def view_parte_incidencia(request:HttpRequest, parte_id:int):
    parte = Parte_Incidencia.objects.filter(ParteIncidenciaID=parte_id).select_related(
        'usuario_creador', 'usuario_asignado', 'cliente', 'empresa'
    ).first()

    if not parte:
        messages.error(request, 'No se encontró la incidencia solicitada.', extra_tags='error')
        return redirect('/backoffice/partes_incidencia')

    context = {'parte': parte}
    return render(request, 'informes/incidencia/pdfview.html', context)