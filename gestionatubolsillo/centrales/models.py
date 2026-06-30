from django.db import models
from users.models import User, tiene_acceso
from encrypted_fields import EncryptedCharField,EncryptedEmailField
# Create your models here.
class Central(models.Model):
    CentralID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    #Datos sensibles
    telefono = EncryptedCharField(max_length=20,blank=True,null=True)
    mail = EncryptedEmailField(blank=True,null=True)
    persona_de_contacto = models.CharField(max_length=200, blank=True)
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    #Relacion con usuario
    usuario_creador = models.ForeignKey('users.User', on_delete=models.SET_NULL,related_name='centrales_creadas',null=True)
    cuenta = models.ForeignKey('users.Cuenta',on_delete=models.SET_NULL,null=True,blank=True,related_name='centrales')

    def __str__(self):
        return self.nombre

def can_view_centrales(user: User)-> bool:
    return tiene_acceso(user, 'CEN')

def can_CRUD_centrales(user: User)-> bool:
    return tiene_acceso(user, 'CEN', nivel_min='2')