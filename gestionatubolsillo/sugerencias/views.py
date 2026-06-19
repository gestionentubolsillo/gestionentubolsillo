from django.shortcuts import render, redirect
from django.http import HttpRequest,HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import can_access_backoffice, User
from .models import Sugerencia, can_view_sugerencias, can_CRUD_sugerencias
from django.core.paginator import Paginator
from django.template import loader
from django.contrib import messages
from empresas.models import Empresa
from django.utils.timezone import now
from django.db.models.manager import BaseManager

DEFAULT_PAGINATION_SUGERENCIAS = 25

# Create your views here.

def validate_sugerencia(request:HttpRequest, texto, usuario_referente_id)->bool:
    errors = False
    user_ref = User.objects.filter(UserID=usuario_referente_id).first()
    if texto == '':
        messages.error(request, 'El texto de la sugerencia no puede estar vacío.',extra_tags='error')
        errors = True
    if not user_ref:
        messages.error(request, 'El usuario referente no es válido.',extra_tags='error')
        errors = True
    return errors

def paginate_sugerencias(request:HttpRequest,sugerencias:BaseManager[Sugerencia]):
    choices = Sugerencia._meta.get_field('estado').choices
    user:User = request.user
    empresas = Empresa.objects.filter(usuario_creador=user)
    #TOREFACTOR: Solo seleccionar los usuarios que pertenecen a una misma cuenta
    users = User.objects.all()
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_SUGERENCIAS
    n_sugerencias = request.GET.get('n_sugerencias', DEFAULT_PAGINATION_SUGERENCIAS)
    paginator = Paginator(sugerencias, n_sugerencias)
    page_obj = paginator.get_page(n_pagina)
    context = {
        'sugerencias': page_obj,
        'page_obj': page_obj,
        'n_pagina': n_pagina,
        'n_sugerencias': n_sugerencias,
        'estados':choices,
        'empresas':empresas,
        'usuarios':users
    }
    return context

def filtra_sugerencias(request:HttpRequest,filter_only_self=False)->tuple[dict,dict]:
    user:User = request.user
    empresa:Empresa = user.empresa
    filtros = {'empresa':empresa}
    exclusiones = {}

    user_creador_id = request.GET.get('usuario_creador_id')
    if filter_only_self:
        filtros['usuario_creador'] = user
    elif user_creador_id:
        user = User.objects.filter(UserID=user_creador_id).first()
        filtros['usuario_creador'] = user

    estado = request.GET.get('estado')
    if estado:
        filtros['estado']=estado
    else:
        exclusiones['estado']= 'borrada'

    id_empresa = request.GET.get('empresa_id')
    if id_empresa:
        empresa = Empresa.objects.filter(EmpresaID=id_empresa).first()
        filtros['empresa']=empresa

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    if fecha_inicio:
        filtros['fecha_creacion__gte'] = fecha_inicio
    if fecha_fin:
        filtros['fecha_creacion__lte'] = fecha_fin

    user_ref_id = request.GET.get('user_ref_id')
    if user_ref_id:
        user = User.objects.filter(UserID=user_ref_id).first()
        filtros['usuario_referente']=user

    return filtros, exclusiones

#unico servicio de backoffice es el listado de sugerencias y la opcion de cambiar su estado
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_sugerencias)
def list_sugerencias(request: HttpRequest):

    filtros, exclusiones=filtra_sugerencias(request)
    sugerencias = Sugerencia.objects.filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_sugerencias(request,sugerencias)
    return render(request,'sugerencias/list.html', context)

#Listado de sugerencias creadas por el usuario, independientemente de si tiene acceso al backoffice
@login_required
@user_passes_test(can_view_sugerencias)
def list_own_sugerencias(request: HttpRequest):

    filtros, exclusiones = filtra_sugerencias(request,filter_only_self=True)
    sugerencias = Sugerencia.objects.filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_sugerencias(request,sugerencias)
    return render(request,'sugerencias/list.html', context)

#No es necesario acceder al backoffice para crear sugerencias
@login_required
@user_passes_test(can_CRUD_sugerencias)
def create_sugerencia(request:HttpRequest):
    user:User = request.user
    #TOREFACTOR: añadir clase cuenta y filtrar por usuarios donde user.cuenta = allowed_users.cuenta
    allowed_users = User.objects.all()
    template = loader.get_template('sugerencias/form.html')
    context = {'action':'create','usuarios':allowed_users}
    if request.method == 'POST':
        created_at = now()
        texto = request.POST.get('texto','')
        departamento = request.POST.get('departamento')
        usuario_referente_id = request.POST.get('user_ref_id')
        errors = validate_sugerencia(request,texto,usuario_referente_id)
        if errors:
            return HttpResponse(template.render(context,request))
        if departamento == '':
            departamento = 'Sin Departamento'
        user_ref = User.objects.filter(UserID=usuario_referente_id).first()
        empresa : Empresa = user_ref.empresa
        sugerencia = Sugerencia()
        sugerencia.texto = texto
        sugerencia.departamento = departamento
        sugerencia.usuario_creador = user
        sugerencia.usuario_referente = user_ref
        sugerencia.empresa = empresa
        sugerencia.fecha_creacion = created_at
        sugerencia.estado = 'pendiente'
        sugerencia.save()
        return redirect('/backoffice/sugerencias')
    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_sugerencias)
def update_estado_sugerencia(request:HttpRequest, sugerencia_id):
    sugerencia = Sugerencia.objects.filter(SugerenciaID=sugerencia_id).first()
    estado = request.POST.get('estado','pendiente')
    sugerencia.estado = estado
    sugerencia.save()
    messages.success(request, 'El estado de la sugerencia ha sido actualizado exitosamente.',extra_tags='success')
    return redirect('/backoffice/sugerencias')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_sugerencias)
def delete_sugerencia(request:HttpRequest, sugerencia_id):
    sugerencia = Sugerencia.objects.filter(SugerenciaID=sugerencia_id).first()
    sugerencia.estado = 'borrada'
    sugerencia.save()
    messages.success(request, 'La sugerencia ha sido borrada exitosamente.',extra_tags='success')
    return redirect('/backoffice/sugerencias')


@login_required
@user_passes_test(can_view_sugerencias)
def details_sugerencia(request:HttpRequest,sugerencia_id):
    sugerencia = Sugerencia.objects.filter(SugerenciaID=sugerencia_id).first()
    if not sugerencia:
        messages.error(request,"La Sugerencia no existe", extra_tags='error')
        return redirect('/backoffice/sugerencias')
    template = loader.get_template('sugerencias/form.html')
    context = {'action': 'view','sugerencia': sugerencia}

    return HttpResponse(template.render(context,request))



    

