from typing import TypedDict
from users.models import User,Cuenta
from .models import Almacen_Item
from datetime import datetime

class ItemData(TypedDict):
    nombre:str
    descripcion:str
    stock:int
    precio_unitario:float
    proveedor:str

def build_item(data:ItemData,creador:User,cuenta:Cuenta,created_at:datetime,item: Almacen_Item | None = None):
    if not item:
        item = Almacen_Item()
        item.fecha_creacion = created_at
        item.usuario_creador = creador
        item.cuenta = cuenta
    item.nombre = data.get('nombre')
    item.descripcion = data.get('descripcion')
    item.stock = data.get('stock')
    item.precio_unitario = data.get('precio_unitario')
    item.proveedor = data.get('proveedor')
    item.save()