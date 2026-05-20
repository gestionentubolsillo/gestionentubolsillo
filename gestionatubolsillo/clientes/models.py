from django.db import models

# Create your models here.

class Cliente(models.Model):
    ClienteID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    cif = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    persona_contacto = models.CharField(max_length=100, blank=True, null=True)

    #Campos que necesitan de API de localización para su funcionamiento
    provincia = models.CharField(max_length=100, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.nombre