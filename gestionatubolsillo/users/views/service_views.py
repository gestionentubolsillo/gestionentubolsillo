from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import User,can_access_backoffice, can_view_users, can_CRUD_users
from django.template import loader
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from servicios.models import Servicio
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from enum import Enum

# Create your views here.

from users.paginators import paginate_servicios_users
from users.validators import validate_services_of_user,validate_account_access

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
@require_http_methods(["GET","POST"])
def assign_services_to_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    auth_error = validate_account_access(request, user)
    if auth_error:
        return auth_error

    return _change_user_servicios(request,user,action=ServicioAccionUser.ADD)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
@require_GET
def list_services_of_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    auth_error = validate_account_access(request, user)
    if auth_error:
        return auth_error

    context = paginate_servicios_users(request,user)
    return render(request,'account/users/services/list.html', context)


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
@require_POST
def remove_services_to_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    auth_error = validate_account_access(request, user)
    if auth_error:
        return auth_error

    return _change_user_servicios(request,user,action=ServicioAccionUser.REMOVE)

class ServicioAccionUser(Enum):
    ADD = 'add',
    REMOVE = 'remove'


def _change_user_servicios(request:HttpRequest,user:User,action:ServicioAccionUser):
    template = loader.get_template('account/users/services/form.html')

    if action == ServicioAccionUser.ADD:
        allowed_servicios = Servicio.objects.filter(empresa=user.empresa)
        context = {'servicios':allowed_servicios,'usuario':user}
    elif action == ServicioAccionUser.REMOVE:
        context = {}


    if request.method == 'POST':
        servicios_ids = request.POST.getlist('servicios_ids')
        try:
            servicios = Servicio.objects.filter(ServicioID__in=servicios_ids)
        except ValueError:
            servicios = Servicio.objects.none()
        errors = validate_services_of_user(request,user,servicios,len(servicios_ids))
        if errors:
            return  HttpResponse(template.render(context,request)) if action == ServicioAccionUser.ADD else redirect(f"/backoffice/users/{str(user.UserID)}/services")
        

        if action == ServicioAccionUser.ADD:
            user.servicios.add(*servicios)
        elif action == ServicioAccionUser.REMOVE:
             user.servicios.remove(*servicios)

        return redirect(f"/backoffice/users/{str(user.UserID)}/services")

    elif request.method == 'GET':
        #ADD Only
        return HttpResponse(template.render(context,request))