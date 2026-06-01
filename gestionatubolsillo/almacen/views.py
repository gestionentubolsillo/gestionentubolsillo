from django.shortcuts import redirect, render
from django.http import HttpRequest,HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import can_access_backoffice, User
from .models import Almacen_Item, can_view_almacen, can_CRUD_almacen
from django.core.paginator import Paginator
from django.template import loader
from django.utils.timezone import now
from django.contrib import messages

DEFAULT_PAGINATION_ALMACEN = 25
# Create your views here.

def validate_almacen_item(request:HttpRequest,nombre,stock,precio_unitario)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe indicar un nombre al item de almacén",extra_tags='error')
        errors = True
    if stock and int(stock) < 0:
        messages.error(request,"El stock no puede ser negativo",extra_tags='error')
        errors = True
    if precio_unitario and float(precio_unitario) < 0:
        messages.error(request,"El precio unitario no puede ser negativo",extra_tags='error')
        errors = True
    return errors

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_almacen)
def list_almacen(request: HttpRequest):
    user:User = request.user
    almacen_items = Almacen_Item.objects.filter(usuario_creador_id = user.UserID)
    n_pagina = request.GET.get('page',1)
    global DEFAULT_PAGINATION_ALMACEN
    n_almacen_items = request.GET.get('n_almacen_items', DEFAULT_PAGINATION_ALMACEN)
    paginacion = Paginator(almacen_items,n_almacen_items)
    page_obj = paginacion.get_page(n_pagina)
    context = {
        'almacen_items': page_obj,
        'page_obj': page_obj,
        'page':n_pagina,
        'n_almacen_items':n_almacen_items
    }
    return render(request,'list.html',context)

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_almacen)
def create_almacen_item(request: HttpRequest):
    if request.method == 'POST':
        created_at = now()
        nombre = request.POST.get('nombre','')
        descripcion = request.POST.get('descripcion','')
        stock = request.POST.get('stock',0)
        precio_unitario = request.POST.get('precio_unitario',0.00)
        proveedor = request.POST.get('proveedor','')
        errors = validate_almacen_item(request,nombre,stock,precio_unitario)
        if errors:
            template = loader.get_template('form.html')
            context = {}
            return HttpResponse(template.render(context,request))
        almacen_item = Almacen_Item()
        almacen_item.nombre = nombre
        almacen_item.descripcion = descripcion
        almacen_item.stock = stock
        almacen_item.precio_unitario = precio_unitario
        almacen_item.proveedor = proveedor
        almacen_item.usuario_creador = request.user
        almacen_item.fecha_creacion = created_at
        almacen_item.save()
        return redirect('backoffice/almacen')
    elif request.method == 'GET':
        template = loader.get_template('form.html')
        context = {}
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_almacen)
def edit_almacen_item(request: HttpRequest, item_id):
    almacen_item = Almacen_Item.objects.filter(AlmacenID=item_id).first()
    if request.method == 'POST':
        nombre = request.POST.get('nombre','')
        descripcion = request.POST.get('descripcion','')
        stock = request.POST.get('stock',0)
        precio_unitario = request.POST.get('precio_unitario',0.00)
        proveedor = request.POST.get('proveedor','')
        errors = validate_almacen_item(request,nombre,stock,precio_unitario)
        if errors:
            template = loader.get_template('form.html')
            context = {}
            return HttpResponse(template.render(context,request))
        almacen_item.nombre = nombre
        almacen_item.descripcion = descripcion
        almacen_item.stock = stock
        almacen_item.precio_unitario = precio_unitario
        almacen_item.proveedor = proveedor
        almacen_item.save()
        return redirect('backoffice/almacen')
    elif request.method == 'GET':
        context = {
            'almacen_item': almacen_item,
            'action':'edit'
        }
        template = loader.get_template('form.html')
        return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_CRUD_almacen)
def delete_almacen_item(request: HttpRequest, item_id):
    almacen_item = Almacen_Item.objects.filter(AlmacenID=item_id).first()
    almacen_item.delete()
    messages.success(request,"Item de almacén eliminado correctamente",extra_tags='success')
    return redirect('backoffice/almacen')

@login_required
@user_passes_test(can_access_backoffice)
@user_passes_test(can_view_almacen)
def almacen_item_details(request: HttpRequest, item_id):
    almacen_item = Almacen_Item.objects.filter(AlmacenID=item_id).first()
    if not almacen_item:
        messages.error(request,"El item de almacén no existe",extra_tags='error')
        return redirect('backoffice/almacen')
    context = {
        'almacen_item': almacen_item,
        'action':'view'
    }
    return render(request,'form.html',context)