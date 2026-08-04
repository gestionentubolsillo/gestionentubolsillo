from django.shortcuts import redirect, render
from django.http import HttpRequest,HttpResponse
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import can_access_backoffice, User
from .models import MedioAuxiliar, can_view_medios_auxiliares, can_CRUD_medios_auxiliares
from django.core.paginator import Paginator
from django.template import loader
from django.utils.timezone import now
from django.contrib import messages

from .paginators import paginate_medios
from .validators import validate_medio_auxiliar, validate_medio_auth

from auditloggers.handlers import save_log
# Create your views here.



@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_medios_auxiliares)
@require_GET
def list_medios_auxiliares(request:HttpRequest):
    user:User = request.user
    medios_auxiliares = MedioAuxiliar.objects.filter(cuenta = user.cuenta).order_by('MedioAuxiliarID')
    context = paginate_medios(request, medios_auxiliares)
    return render(request,'mediosaux/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_medios_auxiliares)
@require_http_methods(["GET","POST"])
def create_medio_auxiliar(request:HttpRequest):
    if request.method == 'POST':
        created_at = now()
        nombre = request.POST.get('nombre','')
        errors = validate_medio_auxiliar(request,nombre)
        if errors:
            template = loader.get_template('mediosaux/form.html')
            context = {'action':'create'}
            return HttpResponse(template.render(context,request))
        medio_auxiliar = MedioAuxiliar()
        medio_auxiliar.nombre = nombre
        medio_auxiliar.fecha_creacion = created_at
        medio_auxiliar.usuario_creador = request.user
        medio_auxiliar.cuenta = request.user.cuenta
        medio_auxiliar.save()
        save_log(request, apartado='MEDIO_AUXILIAR', accion='CREATE', id_user=request.user.pk, id_cuenta=medio_auxiliar.cuenta.pk,info=f'Medio auxiliar creado con ID: {medio_auxiliar.MedioAuxiliarID}')
        return redirect('/backoffice/medios_auxiliares')
    elif request.method == 'GET':
        template = loader.get_template('mediosaux/form.html')
        context = {'action':'create'}
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_medios_auxiliares)
@require_http_methods(["GET","POST"])
def edit_medio_auxiliar(request:HttpRequest, medio_auxiliar_id):
    medio_auxiliar = MedioAuxiliar.objects.filter(MedioAuxiliarID=medio_auxiliar_id).first()
    auth_error = validate_medio_auth(request,medio_auxiliar)
    if auth_error:
        save_log(request, apartado='MEDIO_AUXILIAR', accion='UNAUTH', id_user=request.user.pk, id_cuenta=medio_auxiliar.cuenta.pk,info=f'Intento de editar medio auxiliar con ID: {medio_auxiliar.MedioAuxiliarID} sin autorización')
        return auth_error
    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        errors = validate_medio_auxiliar(request,nombre)
        if errors:
            save_log(request, apartado='MEDIO_AUXILIAR', accion='ERROR', id_user=request.user.pk, id_cuenta=medio_auxiliar.cuenta.pk,info=f'Error al editar medio auxiliar con ID: {medio_auxiliar.MedioAuxiliarID}')
            template = loader.get_template('mediosaux/form.html')
            context = {
                'medio_auxiliar': medio_auxiliar,
                'action':'edit'
            }
            return HttpResponse(template.render(context,request))
        medio_auxiliar.nombre = nombre
        medio_auxiliar.save()
        save_log(request, apartado='MEDIO_AUXILIAR', accion='UPDATE', id_user=request.user.pk, id_cuenta=medio_auxiliar.cuenta.pk,info=f'Medio auxiliar editado con ID: {medio_auxiliar.MedioAuxiliarID}')
        return redirect('/backoffice/medios_auxiliares')
    elif request.method == 'GET':
        template = loader.get_template('mediosaux/form.html')
        context = {
            'medio_auxiliar': medio_auxiliar,
            'action':'edit'
        }
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_medios_auxiliares)
@require_POST
def delete_medio_auxiliar(request:HttpRequest, medio_auxiliar_id):
    medio_auxiliar = MedioAuxiliar.objects.filter(MedioAuxiliarID=medio_auxiliar_id).first()
    auth_error = validate_medio_auth(request,medio_auxiliar)
    if auth_error:
        save_log(request, apartado='MEDIO_AUXILIAR', accion='UNAUTH', id_user=request.user.pk, id_cuenta=medio_auxiliar.cuenta.pk,info=f'Intento de eliminar medio auxiliar con ID: {medio_auxiliar.MedioAuxiliarID} sin autorización')
        return auth_error
    save_log(request, apartado='MEDIO_AUXILIAR', accion='DELETE', id_user=request.user.pk, id_cuenta=medio_auxiliar.cuenta.pk,info=f'Medio auxiliar eliminado con ID: {medio_auxiliar.MedioAuxiliarID}')
    medio_auxiliar.delete()
    messages.success(request,"Medio auxiliar eliminado correctamente",extra_tags='success')
    return redirect('/backoffice/medios_auxiliares')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_medios_auxiliares)
@require_GET
def medio_auxiliar_details(request:HttpRequest, medio_auxiliar_id):
    medio_auxiliar = MedioAuxiliar.objects.filter(MedioAuxiliarID=medio_auxiliar_id).first()
    auth_error = validate_medio_auth(request,medio_auxiliar)
    if auth_error:
        save_log(request, apartado='MEDIO_AUXILIAR', accion='UNAUTH', id_user=request.user.pk, id_cuenta=medio_auxiliar.cuenta.pk,info=f'Intento de ver detalles de medio auxiliar con ID: {medio_auxiliar.MedioAuxiliarID} sin autorización')
        return auth_error
    context = {
        'medio_auxiliar': medio_auxiliar,
        'action':'view'
    }
    return render(request,'mediosaux/form.html',context)
