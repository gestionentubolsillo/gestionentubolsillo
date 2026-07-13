from django.http import HttpRequest,HttpResponse
from django.template import loader
from django.contrib import messages

from django.utils.timezone import now
from django.contrib.auth.decorators import login_required,user_passes_test
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from users.models import User, can_access_backoffice

from partes.models import Informe_Acuda, can_view_acuda, can_CRUD_acuda
from partes.filters import filtra_informes_acuda
from partes.paginators import paginate_informes
from partes.validators import validate_parte_acuda
from partes.builders import build_parte_acuda

from clientes.models import Cliente
from centrales.models import Central


@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_acuda)
@require_GET
def list_inf_acuda(request:HttpRequest):
    filtros, exclusiones = filtra_informes_acuda(request)
    partes = Informe_Acuda.objects.filter(**filtros).exclude(**exclusiones).order_by('-fecha_creacion')
    context = paginate_informes(request,partes)
    return render(request,'informes/acuda/list.html',context)

@login_required
@user_passes_test(can_CRUD_acuda)
@require_http_methods(["GET","POST"])
def create_inf_acuda(request:HttpRequest):
    user:User = request.user
    template = loader.get_template('informes/acuda/form.html')
    allowed_users = User.objects.filter(cuenta=user.cuenta, is_active=True)
    allowed_clientes = Cliente.objects.filter(cuenta=user.cuenta)
    allowed_centrales = Central.objects.filter(cuenta=user.cuenta)
    context = {
        'usuarios': allowed_users,
        'clientes': allowed_clientes,
        'centrales': allowed_centrales,
        'action': 'create',
    }
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        usuario_id = request.POST.get('usuario_id')
        central_id = request.POST.get('central_id')
        descripcion = request.POST.get('descripcion','')
        errors = validate_parte_acuda(request,cliente_id,usuario_id,central_id,descripcion)
        if errors:
            return HttpResponse(template.render(context,request))
        created_at = now()
        parte = build_parte_acuda(data={
            'general':{
                'usuario_asignado':User.objects.get(UserID=usuario_id),
                'cliente':Cliente.objects.get(ClienteID=cliente_id),
                'empresa':User.objects.get(UserID=usuario_id).empresa
            },
            'central':Central.objects.get(CentralID=central_id),
            'descripcion':descripcion
        },user=user,created_at=created_at)
        return redirect('/backoffice/informes_acuda')
    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))

@require_GET
def view_parte_acuda(request:HttpRequest, parte_id:int):
    parte = Informe_Acuda.objects.filter(InformeAcudaID=parte_id).select_related(
        'usuario_creador', 'usuario_asignado', 'cliente', 'empresa', 'central'
    ).first()

    if not parte:
        messages.error(request, 'No se encontró el informe de Acuda solicitado.', extra_tags='error')
        return redirect('/backoffice/informes_acuda')

    context = {'parte': parte}
    return render(request, 'informes/acuda/pdfview.html', context)

@require_GET
def parte_acuda_details(request:HttpRequest,parte_id:int):
    parte = Informe_Acuda.objects.filter(InformeAcudaID=parte_id).select_related(
        'usuario_creador', 'usuario_asignado', 'cliente', 'empresa', 'central'
    ).first()
    context = {'parte': parte, 'action':'view'}
    return render(request, 'informes/acuda/form.html', context)