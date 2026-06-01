from django.db import models
from users.models import User

# Create your models here.

class Almacen_Item(models.Model):
    AlmacenID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    stock = models.IntegerField(default=0)
    #Precio unitario en euros, con dos decimales
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    proveedor = models.CharField(max_length=200, blank=True)

    usuario_creador = models.ForeignKey('users.User', on_delete=models.SET_NULL,related_name='almacen_items_creados',null=True)


def can_view_almacen(user: User)->bool:
    return user.permisos_almacen == 'view_only' or user.permisos_almacen == 'create_modify'

def can_CRUD_almacen(user: User)->bool:
    return user.permisos_almacen == 'create_modify'
