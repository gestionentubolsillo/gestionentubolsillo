from django.db import models
from users.models import User, tiene_acceso

# Create your models here.
class Sugerencia(models.Model):
    Estado_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('solucionada', 'Solucionada'),
        ('borrada', 'Borrada')
    ]
    SugerenciaID = models.AutoField(primary_key=True)
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    departamento = models.CharField(max_length=100, blank=True)
    usuario_creador = models.ForeignKey('users.User', on_delete=models.SET_NULL,related_name='sugerencias_creadas',null=True)
    usuario_referente = models.ForeignKey('users.User', on_delete=models.SET_NULL,related_name='sugerencias_referente',null=True)
    estado = models.CharField(max_length=20, choices=Estado_CHOICES, default='pendiente')
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='sugerencias_empresa')

def can_view_sugerencias(user: User)-> bool:
    return tiene_acceso(user, 'SUG')

def can_CRUD_sugerencias(user: User)-> bool:
    return tiene_acceso(user, 'SUG', nivel_min='2')