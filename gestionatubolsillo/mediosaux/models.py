from django.db import models
from users.models import User

# Create your models here.

class MedioAuxiliar(models.Model):
    MedioAuxiliarID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creador = models.ForeignKey('users.User', on_delete=models.SET_NULL,related_name='medios_auxiliares_creados',null=True)


def can_view_medios_auxiliares(user: User)->bool:
    return user.permisos_medios_auxiliares == 'view_only' or user.permisos_medios_auxiliares == 'create_modify'

def can_CRUD_medios_auxiliares(user: User)->bool:
    return user.permisos_medios_auxiliares == 'create_modify'

