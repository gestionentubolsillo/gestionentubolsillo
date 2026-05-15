from django.db import models

# Create your models here.
class ParteTrabajo(models.Model):
    ParteTrabajoID = models.AutoField(primary_key=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    #Relacion N:1 con el modelo User
    #Un parte de trabajo es creado por un unico usuario, pero un usuario puede crear varios partes de trabajo
    usuario_creador = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='partes_trabajo_creados')

    #Los partes en general contienen un campo de texto con la descripción del parte, pero también admite fotos para documentar el parte
    descripcion = models.TextField(blank=True, null=True)
    #TO-DO: Cambiar ruta de subida de fotos
    foto = models.ImageField(upload_to='partes_trabajo_fotos/', blank=True, null=True)
