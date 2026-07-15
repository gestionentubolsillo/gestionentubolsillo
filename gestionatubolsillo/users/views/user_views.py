from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import User,can_access_backoffice, can_view_users, can_CRUD_users
from django.template import loader
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from empresas.models import Empresa
from decimal import Decimal
from django.views.decorators.http import require_POST, require_GET, require_http_methods
# Create your views here.

from users.filters import filter_users
from users.paginators import paginate_users
from users.builders import build_user
from users.validators import validate_user,validate_user_edit,validate_account_access


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
@require_http_methods(["GET","POST"])
def create_user(request:HttpRequest):
    return _create_or_modify_user(request)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
@require_GET
def lista_users(request:HttpRequest):
    
    filtros, exclusiones = filter_users(request)
    lista_usuarios = User.objects.filter(**filtros).exclude(**exclusiones).order_by('UserID')
    context = paginate_users(request,lista_usuarios)

    return render(request,'account/users/list.html', context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_users)
@require_GET
def user_details(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    if not user:
        messages.error(request,"El usuario no existe",extra_tags='error')
        return redirect('/backoffice/users')

    auth_error = validate_account_access(request, user)
    if auth_error:
        return auth_error

    context = {'action':'view','usuario':user}
    return render(request,'account/users/form.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
@require_http_methods(["GET","POST"])
def edit_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    auth_error = validate_account_access(request, user)
    if auth_error:
        return auth_error

    return _create_or_modify_user(request,user)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_users)
@require_POST
def delete_user(request:HttpRequest,user_id):
    user = User.objects.filter(UserID=user_id).first()
    auth_error = validate_account_access(request, user)
    if auth_error:
        return auth_error

    user.delete()
    messages.success(request,"El usuario ha sido eliminado correctamente",extra_tags='success')
    return redirect('/backoffice/users')

def _create_or_modify_user(request:HttpRequest,user:User|None = None):

    template = loader.get_template('account/users/form.html')
    logged_user:User=request.user
    empresas = Empresa.objects.filter(usuario_creador_id=logged_user.UserID)
    categorias = User._meta.get_field('categoria').choices
    if user is None:
        context = {'action':'create','empresas':empresas,'categorias_choices':categorias}
    else:
        context = {'usuario':user,'action':'edit','categorias_choices':categorias,'empresas':empresas}

    if request.method == 'POST':
        usuario = request.POST.get('username','')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('password_confirm','')
        nombre = request.POST.get('nombre','')
        apellidos = request.POST.get('apellidos','')
        mail = request.POST.get('mail','')
        direccion = request.POST.get('direccion','')
        provincia = request.POST.get('provincia','')
        municipio = request.POST.get('municipio','')
        telefono = request.POST.get('telefono','')
        nif = request.POST.get('nif','')
        empresa = request.POST.get('empresa','')
        check_es_inspector = request.POST.get('es_inspector') == 'on'
        check_es_inspector_de_trabajo = request.POST.get('es_inspector_trabajo') == 'on'
        delegacion = request.POST.get('delegacion','')
        categoria = request.POST.get('categoria','ejecutivo')
        precio_hora = Decimal(request.POST.get('precio_hora') or 0.)
        always_track_gps = request.POST.get('track_gps') == 'on'
        comentarios = request.POST.get('comentarios','')


        errors:bool= False
        if user is None:
            errors = validate_user(request,usuario,password,confirm_password,nombre,apellidos,provincia,municipio, empresa)
        else:
            errors = validate_user_edit(request,usuario,nombre,apellidos,provincia,municipio, empresa)
        if errors:
            return HttpResponse(template.render(context,request))
        
        user_empresa = Empresa.objects.filter(EmpresaID=empresa).first()
        user = build_user(data={
            'username':usuario,
            'password':password,
            'first_name':nombre,
            'last_name':apellidos,
            'email':mail,
            'direccion':direccion,
            'provincia':provincia,
            'municipio':municipio,
            'nif':nif,
            'telefono':telefono,
            'categoria':categoria,
            'always_track_GPS':always_track_gps,
            'comentarios':comentarios,
            'empresa':user_empresa,
            'esInspector':check_es_inspector,
            'esInspector_parteTrabajo':check_es_inspector_de_trabajo,
            'precio_hora':precio_hora,
            'cuenta':logged_user.cuenta
        },user=user)
        return redirect("/backoffice/users/"+str(user.UserID))


    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))
