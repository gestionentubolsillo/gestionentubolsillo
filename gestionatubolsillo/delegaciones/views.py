from django.shortcuts import redirect, render
from django.http import HttpRequest,HttpResponse
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import can_access_backoffice, User
from .models import Delegacion
from django.template import loader
from django.utils.timezone import now
from django.contrib import messages


from .filters import filter_delegaciones
from .paginators import paginate_delegaciones
from .builders import build_delegacion
from .validators import validate_delegacion, validate_auth_delegacion


# Create your views here.
@login_required
@user_passes_test(can_access_backoffice)
@require_GET
def list_delegaciones(request: HttpRequest):
    
    filtros,exclusiones = filter_delegaciones(request)
    delegaciones = Delegacion.objects.filter(**filtros).exclude(**exclusiones).order_by('DelegacionID')
    context = paginate_delegaciones(request,delegaciones)
    return render(request,'delegaciones/list.html',context)

@require_http_methods(["GET","POST"])
def create_delegacion(request: HttpRequest):
    return _create_or_modify_delegacion(request)
    
@login_required
@user_passes_test(can_access_backoffice)
@require_POST
def delete_delegacion(request: HttpRequest, delegacion_id):
    delegacion = Delegacion.objects.filter(DelegacionID=delegacion_id).first()
    auth_error = validate_auth_delegacion(request,delegacion)
    if auth_error:
        return auth_error
    delegacion.delete()
    messages.success(request, 'La delegación ha sido borrada exitosamente.',extra_tags='success')
    return redirect('/backoffice/delegaciones')

@login_required
@user_passes_test(can_access_backoffice)
@require_http_methods(["GET","POST"])
def edit_delegacion(request: HttpRequest, delegacion_id):
    delegacion = Delegacion.objects.filter(DelegacionID=delegacion_id).first()
    auth_error = validate_auth_delegacion(request,delegacion)
    if auth_error:
        return auth_error
    return _create_or_modify_delegacion(request,delegacion)
    

@login_required
@user_passes_test(can_access_backoffice)
@require_GET
def delegacion_details(request: HttpRequest, delegacion_id):
    delegacion = Delegacion.objects.filter(DelegacionID=delegacion_id).first()
    auth_error = validate_auth_delegacion(request,delegacion)
    if auth_error:
        return auth_error
    context={
        'delegacion':delegacion,
        'action':'view'
    }
    return render(request,'delegaciones/form.html',context)


def _create_or_modify_delegacion(request:HttpRequest,delegacion:Delegacion|None = None):

    template = loader.get_template('delegaciones/form.html')
    if delegacion is None:
        context = {'action':'create'}
    else:
        context = {'delegacion':delegacion,'action':'edit'}

    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        user : User = request.user
        errors = validate_delegacion(request,nombre)
        if errors:
            return HttpResponse(template.render(context,request))
        created_at = now()
        build_delegacion(data={
            'nombre':nombre,
            'user':user
        },created_at=created_at,delegacion=delegacion)
        return redirect('/backoffice/delegaciones')
        
    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))