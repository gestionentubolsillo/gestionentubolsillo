from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import User,PermisosModulo,can_access_backoffice, can_view_users, can_CRUD_users
from django.template import loader
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.views.decorators.http import require_GET, require_http_methods


# Create your views here.

from users.builders import build_permissions
from users.validators import validate_perms,validate_account_access

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
@require_http_methods(["GET","POST"])
def alter_user_permissions(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    auth_error = validate_account_access(request, user)
    if auth_error:
        return auth_error
    
    template = loader.get_template('account/users/permissions/form.html')
    context = {
            'usuario':user,
            'action':'edit',
            'choices':User.PERMISSIONS_CHOICES,
            'modulos': PermisosModulo.MODULOS,
            'niveles': PermisosModulo.NIVELES,
            'permisos': [(permiso.modulo, permiso.nivel) for permiso in user.permisos.all()],
        }

    if request.method == 'POST':
        p_dashboard = request.POST.get('p_dashboard') == 'on'
        p_login = request.POST.get('p_login') == 'on'
        p_view_self_trabajo = request.POST.get('p_view_self_trabajo') == 'on'

        permisos = {
            'USR': request.POST.get('p_USR', '0'),
            'TAR': request.POST.get('p_TAR', '0'),
            'CLI': request.POST.get('p_CLI', '0'),
            'NFC': request.POST.get('p_NFC', '0'),
            'CEN': request.POST.get('p_CEN', '0'),
            'MED': request.POST.get('p_MED', '0'),
            'SUG': request.POST.get('p_SUG', '0'),
            'PAR': request.POST.get('p_PAR', '0'),
            'INC': request.POST.get('p_INC', '0'),
            'ACU': request.POST.get('p_ACU', '0'),
            'INS': request.POST.get('p_INS', '0'),
            'MAN': request.POST.get('p_MAN', '0'),
            'ALM': request.POST.get('p_ALM', '0'),
            'INF': request.POST.get('p_INF', '0'),
            'EMP': request.POST.get('p_EMP', '0'),
            'CON': request.POST.get('p_CON', '0'),
        }
        errors = validate_perms(request,permisos)
        if errors:
            return HttpResponse(template.render(context,request))

        user = build_permissions(data={
            'can_view_own_partes_trabajo':p_view_self_trabajo,
            'has_dashboard_access':p_dashboard,
            'has_login_access':p_login,
            'permisos':permisos
        },user=user)
        return redirect("/backoffice/users")

    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))
    
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
@require_GET
def view_user_permissions(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    if not user:
        messages.error(request,"El usuario no existe",extra_tags='error')
        return redirect('/backoffice/users')

    auth_error = validate_account_access(request, user)
    if auth_error:
        return auth_error

    context = {
        'action':'view',
        'usuario':user,
        'modulos': PermisosModulo.MODULOS,
        'niveles': PermisosModulo.NIVELES,
        'permisos': [(permiso.modulo, permiso.nivel) for permiso in user.permisos.all()],
    }
    return render(request,'account/users/permissions/form.html',context)