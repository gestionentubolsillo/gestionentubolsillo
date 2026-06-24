from django.shortcuts import render, redirect
from django.http import HttpRequest,HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import can_access_backoffice, User
from .models import Sugerencia, can_view_sugerencias, can_CRUD_sugerencias

from django.template import loader
from django.contrib import messages
from empresas.models import Empresa
from django.utils.timezone import now

from .filters import filtra_sugerencias
from .paginators import paginate_sugerencias
from .validators import validate_sugerencia
from .builders import build_sugerencia



# Create your views here.

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
        
        user_ref = User.objects.filter(UserID=usuario_referente_id).first()
        build_sugerencia(
            data={
                'texto':texto,
                'departamento':departamento,
                'usuario_creador':user,
                'usuario_referente':user_ref
            },fecha_creacion=created_at
        )
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



    

