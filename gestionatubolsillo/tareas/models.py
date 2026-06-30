from django.db import models
from users.models import User, tiene_acceso

# Create your models here.

class Tarea(models.Model):
    TareaID = models.AutoField(primary_key=True)
    Estado_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('leida', 'Leída'),
        ('en_progreso', 'En progreso'),
        ('terminada', 'Terminada'),
        ('borrada', 'Borrada')
    ]

    texto = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    estado = models.CharField(max_length=20, choices=Estado_CHOICES, default='pendiente')

    es_urgente = models.BooleanField(default=False)
    usuario_creador = models.ForeignKey('users.User',on_delete=models.CASCADE,related_name='tareas_creadas')

    usuario_asignado = models.ForeignKey('users.User',on_delete=models.SET_NULL,related_name='tareas_asignadas', null=True, blank=True )
    servicio_asignado = models.ForeignKey('servicios.Servicio', on_delete=models.SET_NULL,related_name='tareas_asignadas', null=True, blank=True)
    cuenta = models.ForeignKey('users.Cuenta',on_delete=models.SET_NULL,null=True,blank=True,related_name='tareas')



class ListadoUsers(models.Model):
    nombre = models.CharField(max_length=20)
    usuarios = models.ManyToManyField('users.User',related_name='listados')
    cuenta = models.ForeignKey('users.Cuenta',on_delete=models.SET_NULL,null=True,blank=True,related_name='listado_tareas')


def can_view_tareas(user: User)-> bool:
    return tiene_acceso(user, 'TAR')

def can_CRUD_tareas(user: User)-> bool:
    return tiene_acceso(user, 'TAR', nivel_min='2')