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

#unico servicio de backoffice es el listado de sugerencias y la opcion de cambiar su estado
@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_sugerencias)
def list_sugerencias(request: HttpRequest):
    #Listado de todas las sugerencias de los usuarios de una empresa
    #TODO: implementar filtro por departamento
    #TODO: implementar filtro por estado
    #TODO: implementar filtro por usuario referente
    user:User = request.user
    empresa:Empresa = user.empresa
    sugerencias = Sugerencia.objects.filter(empresa=empresa).order_by('-fecha_creacion')
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_SUGERENCIAS
    n_sugerencias = request.GET.get('n_sugerencias', DEFAULT_PAGINATION_SUGERENCIAS)
    paginator = Paginator(sugerencias, n_sugerencias)
    page_obj = paginator.get_page(n_pagina)
    context = {
        'sugerencias': page_obj,
        'page_obj': page_obj,
        'n_pagina': n_pagina,
        'n_sugerencias': n_sugerencias
    }
    return render(request,'list.html', context)

#Listado de sugerencias creadas por el usuario, independientemente de si tiene acceso al backoffice
@login_required
@user_passes_test(can_view_sugerencias)
def list_own_sugerencias(request: HttpRequest):
    #Listado de sugerencias creadas por el usuario logueado
    #TODO: implementar filtro por departamento
    #TODO: implementar filtro por estado
    user:User = request.user
    sugerencias = Sugerencia.objects.filter(usuario_creador=user).order_by('-fecha_creacion')
    n_pagina = request.GET.get('page', 1)
    global DEFAULT_PAGINATION_SUGERENCIAS
    n_sugerencias = request.GET.get('n_sugerencias', DEFAULT_PAGINATION_SUGERENCIAS)
    paginator = Paginator(sugerencias, n_sugerencias)
    page_obj = paginator.get_page(n_pagina)
    context = {
        'sugerencias': page_obj,
        'page_obj': page_obj,
        'n_pagina': n_pagina,
        'n_sugerencias': n_sugerencias
    }
    return render(request,'list.html', context)

#No es necesario acceder al backoffice para crear sugerencias
@login_required
@user_passes_test(can_CRUD_sugerencias)
def create_sugerencia(request:HttpRequest):
    if request.method == 'POST':
        created_at = now()
        texto = request.POST.get('texto','')
        departamento = request.POST.get('departamento','Sin departamento')
        usuario_referente_id = request.POST.get('user_ref_id')
        errors = validate_sugerencia(request,texto,usuario_referente_id)
        if errors:
            template = loader.get_template('form.html')
            context = {}
            return HttpResponse(template.render(context,request))
        user_ref = User.objects.filter(UserID=usuario_referente_id).first()
        empresa : Empresa = user_ref.empresa
        sugerencia = Sugerencia()
        sugerencia.texto = texto
        sugerencia.departamento = departamento
        sugerencia.usuario_creador = request.user
        sugerencia.usuario_referente = user_ref
        sugerencia.empresa = empresa
        sugerencia.fecha_creacion = created_at
        sugerencia.save()
        return redirect('sugerencias/list')
    elif request.method == 'GET':
        template = loader.get_template('form.html')
        context = {}
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
    return redirect('backoffice/sugerencias')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_sugerencias)
def delete_sugerencia(request:HttpRequest, sugerencia_id):
    sugerencia = Sugerencia.objects.filter(SugerenciaID=sugerencia_id).first()
    sugerencia.estado = 'borrada'
    sugerencia.save()
    messages.success(request, 'La sugerencia ha sido borrada exitosamente.',extra_tags='success')
    return redirect('backoffice/sugerencias')


    

