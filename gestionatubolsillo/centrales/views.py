from django.contrib import messages
from django.template import loader
from django.shortcuts import render, redirect
from django.http import HttpRequest,HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import can_access_backoffice, User
from .models import Central, can_view_centrales, can_CRUD_centrales
from django.utils.timezone import now

from .filters import filter_centrales
from .paginators import paginate_centrales
from .builders import build_central
from .validators import validate_central, validate_auth_central


# Create your views here.


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_centrales)
def list_centrales(request: HttpRequest):
    filtros, exclusiones = filter_centrales(request)
    centrales = Central.objects.filter(**filtros).exclude(**exclusiones).order_by('CentralID')
    context = paginate_centrales(request,centrales)
    return render(request,'centrales/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_centrales)
def create_central(request: HttpRequest):
    return _create_or_modify_central(request)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_centrales)
def edit_central(request: HttpRequest, central_id):
    central = Central.objects.filter(CentralID=central_id).first()
    auth_error = validate_auth_central(request,central)
    if auth_error:
        return auth_error
    return _create_or_modify_central(request,central)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_centrales)
def delete_central(request: HttpRequest, central_id):
    central = Central.objects.filter(CentralID=central_id).first()
    auth_error = validate_auth_central(request,central)
    if auth_error:
        return auth_error
    central.delete()
    messages.success(request,"Central receptora eliminada correctamente",extra_tags='success')
    return redirect('/backoffice/centrales')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_centrales)
def central_details(request: HttpRequest, central_id):
    central = Central.objects.filter(CentralID=central_id).first()
    auth_error = validate_auth_central(request,central)
    if auth_error:
        return auth_error
    context = {
        'central': central,
        'action':'view'
    }
    return render(request,'centrales/form.html',context)


def _create_or_modify_central(request:HttpRequest,central:Central | None = None):
    template = loader.get_template('centrales/form.html')
    if central is None:
        context = {'action':'create'}
    else:
        context = {'action':'edit','central': central}
    

    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        telefono = request.POST.get('telefono','')
        mail = request.POST.get('mail','')
        persona_de_contacto = request.POST.get('persona_de_contacto','')
        observaciones = request.POST.get('observaciones','')
        errors = validate_central(request,nombre)
        if errors:
            return HttpResponse(template.render(context,request))
        created_at = now()
        logged_user : User = request.user

        build_central(data={
            'nombre':nombre,
            'contacto':persona_de_contacto,
            'mail':mail,
            'observaciones':observaciones,
            'telefono':telefono
        },created_at=created_at,central=central,cuenta=logged_user.cuenta)

        return redirect('/backoffice/centrales')

    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))