from django.db import models

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
    TIPO_CHOICES = [
        ('normal','Normal'),
        ('urgente','Urgente')
    ]

    TIPO_ASOCIACION_CHOICES = [
        ('empresa', 'Asociada a todos los usuarios de una empresa'),
        ('usuario', 'Asociada a usuario particular')
    ]

    texto = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    #Relacion N:N con el modelo Empresa.
    #Una tarea puede estar asociada a la totalidad de los usuarios de una empresa o de varias empresas
    empresas_asociadas = models.ManyToManyField('empresas.Empresa', related_name='tareas_asociadas')

    #Relacion N:N con el modelo User
    #Un usuario puede tener varias tareas y una tarea puede ser asignada a varios usuarios
    usuarios_asignados = models.ManyToManyField('users.User', related_name='tareas_asignadas')
    estado = models.CharField(max_length=20, choices=Estado_CHOICES, default='pendiente')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='normal')
    tipo_asociacion = models.CharField(max_length=20, choices=TIPO_ASOCIACION_CHOICES, default='usuario')

    def get_usuarios_asociados(self):
        if self.tipo_asociacion == 'usuario':
            return self.usuarios_asignados.all()
        elif self.tipo_asociacion == 'empresa':
            return User.objects.filter(empresa__in=self.empresas_asociadas.all(),is_active=True).distinct()
        return User.objects.none()

