from django.http import HttpRequest
from django.shortcuts import redirect
from django.contrib import messages
from .models import Almacen_Item
from users.models import User

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


def validate_auth_item(request:HttpRequest,item:Almacen_Item):
    logged_user : User = request.user
    if not item:
        messages.error(request,"El objeto no existe",extra_tags='error')
        return redirect('/backoffice/almacen')
    if logged_user.cuenta != item.cuenta:
        return redirect('/AuthError')