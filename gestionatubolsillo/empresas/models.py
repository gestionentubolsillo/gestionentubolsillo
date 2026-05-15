from django.db import models

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


