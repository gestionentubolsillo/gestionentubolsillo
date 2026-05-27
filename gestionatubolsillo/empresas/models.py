from django.db import models
from users.models import User
# Create your models here.

class Empresa(models.Model):

    PAQUETES_CHOICES = [
        ('seguridad', 'Seguridad'),
        ('auxiliares', 'Auxiliares'),
        ('mantenimiento', 'Mantenimiento'),
        ('transportes', 'Transportes')
    ]

    EmpresaID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    paquete = models.CharField(max_length=20, choices=PAQUETES_CHOICES, default=None)
    usuario_creador = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='creador')


def can_view_empresas(user:User)-> bool:
    return user.permisos_empresas == 'view_only' or user.permisos_empresas == 'create_modify'

def can_CRUD_empresas(user:User)->bool:
    return user.permisos_empresas == 'create_modify'


