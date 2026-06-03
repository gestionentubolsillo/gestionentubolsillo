from django.db import models
from users.models import User

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
    #REFACTORED- Eliminado relaciones N:N con Empresa y User
    usuario_asignado = models.ForeignKey('users.User',on_delete=models.CASCADE,related_name='tareas_asignadas')

    def get_usuarios_asociados(self):
        if self.tipo_asociacion == 'usuario':
            return self.usuarios_asignados.all()
        elif self.tipo_asociacion == 'empresa':
            return User.objects.filter(empresa__in=self.empresas_asociadas.all(),is_active=True).distinct()
        return User.objects.none()


def can_view_tareas(user:User)-> bool:
    return user.permisos_tareas == 'view_only' or user.permisos_tareas == 'create_modify'

def can_CRUD_tareas(user:User)->bool:
    return user.permisos_tareas == 'create_modify'