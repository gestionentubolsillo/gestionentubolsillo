from django.db import models
from users.models import User, tiene_acceso
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
    usuario_creador = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='empresas_creadas')
    cuenta = models.ForeignKey('users.Cuenta',on_delete=models.SET_NULL,blank=True,null=True,related_name='empresas')


def can_view_empresas(user: User)-> bool:
    return tiene_acceso(user, 'EMP')

def can_CRUD_empresas(user: User)-> bool:
    return tiene_acceso(user, 'EMP', nivel_min='2')


