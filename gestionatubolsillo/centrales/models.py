from django.db import models

# Create your models here.
class Central(models.Model):
    CentralID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20, blank=True)
    mail = models.EmailField(blank=True)
    persona_de_contacto = models.CharField(max_length=200, blank=True)
    observaciones = models.TextField(blank=True)
    #Relacion con usuario
    usuario_creador = models.ForeignKey('users.User', on_delete=models.SET_NULL,related_name='centrales_creadas',null=True)

    def __str__(self):
        return self.nombre

