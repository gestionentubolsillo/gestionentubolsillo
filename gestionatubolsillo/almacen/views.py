from django.shortcuts import redirect, render
from django.http import HttpRequest,HttpResponse
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import can_access_backoffice, User
from .models import Almacen_Item, can_view_almacen, can_CRUD_almacen

from django.template import loader
from django.utils.timezone import now
from django.contrib import messages

from .paginators import paginate_items
from .validators import validate_almacen_item, validate_auth_item
from .builders import build_item
from decimal import Decimal
# Create your views here.

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_almacen)
@require_GET
def list_almacen(request: HttpRequest):
    user:User = request.user
    almacen_items = Almacen_Item.objects.filter(cuenta=user.cuenta).order_by('AlmacenID')
    context = paginate_items(request,almacen_items)
    
    return render(request,'almacen/list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_almacen)
@require_http_methods(["GET","POST"])
def create_almacen_item(request: HttpRequest):
    return _create_or_modify_item(request)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_almacen)
@require_http_methods(["GET","POST"])
def edit_almacen_item(request: HttpRequest, item_id):
    almacen_item = Almacen_Item.objects.filter(AlmacenID=item_id).first()
    auth_error = validate_auth_item(request,almacen_item)
    if auth_error:
        return auth_error
    return _create_or_modify_item(request,almacen_item)
        

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_almacen)
@require_POST
def delete_almacen_item(request: HttpRequest, item_id):
    almacen_item = Almacen_Item.objects.filter(AlmacenID=item_id).first()
    auth_error = validate_auth_item(request,almacen_item)
    if auth_error:
        return auth_error
    almacen_item.delete()
    messages.success(request,"Item de almacén eliminado correctamente",extra_tags='success')
    return redirect('/backoffice/almacen')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_almacen)
@require_GET
def almacen_item_details(request: HttpRequest, item_id):
    almacen_item = Almacen_Item.objects.filter(AlmacenID=item_id).first()
    auth_error = validate_auth_item(request,almacen_item)
    if auth_error:
        return auth_error
    context = {
        'almacen_item': almacen_item,
        'action':'view'
    }
    return render(request,'almacen/form.html',context)


def _create_or_modify_item(request:HttpRequest,item:Almacen_Item|None=None):
    user : User = request.user
    template = loader.get_template('almacen/form.html')
    if item is None:
        context = {'action':'create'}
    else:
        context = {
            'almacen_item': item,'action':'edit'}
        
    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        descripcion = request.POST.get('descripcion','')
        stock = request.POST.get('stock',0)
        precio_unitario = Decimal(request.POST.get('precio_unitario',0.00))
        proveedor = request.POST.get('proveedor','')
        errors = validate_almacen_item(request,nombre,stock,precio_unitario)
        if errors:
            return HttpResponse(template.render(context,request))
        created_at = now()
        build_item(data={
            'nombre':nombre,
            'descripcion':descripcion,
            'stock':stock,
            'precio_unitario':precio_unitario,
            'proveedor':proveedor
        },creador=user,cuenta=user.cuenta,created_at=created_at,item=item)
        return redirect('/backoffice/almacen')

    elif request.method == 'GET':
        return HttpResponse(template.render(context,request))
    