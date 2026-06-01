from django.db import models
from users.models import User
# Create your models here.
class Delegacion(models.Model):
    DelegacionID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creador = models.ForeignKey('users.User', on_delete=models.SET_NULL,related_name='delegaciones_creadas',null=True)



#No parece que haya una funcionalidad de permisos para delegaciones
#Parece que en algun momento se perdio o algo