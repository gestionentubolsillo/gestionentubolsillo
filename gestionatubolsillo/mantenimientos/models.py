from django.db import models

from users.models import User, tiene_acceso

# Create your models here.

class Mantenimiento_DOC(models.Model):
    MantenimientoID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creador = models.ForeignKey('users.User', on_delete=models.SET_NULL,related_name='mantenimientos_doc_creados',null=True)
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='mantenimientos_doc_empresa')

class Mantenimiento_DOC_GRUPO(models.Model):
    MantenimientoGrupoID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    orden_de_grupo = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creador = models.ForeignKey('users.User', on_delete=models.SET_NULL,related_name='mantenimientos_doc_grupo_creados',null=True)
    documento_mantenimiento = models.ForeignKey('Mantenimiento_DOC', on_delete=models.CASCADE, related_name='grupos_documento')

class Mantenimiento_DOC_CAMPO(models.Model):
    TIPO_DE_CAMPO_CHOICES = [
        ('texto', 'Texto'),
        ('valores_predefinidos', 'valores predefinidos'),
        ('checkbox', 'checkbox'),
        ('checkbox_dos_estados', 'checkbox dos estados'),
    ]
    MantenimientoCampoID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    tipo_de_campo = models.CharField(max_length=50, choices=TIPO_DE_CAMPO_CHOICES, default='texto')
    texto_ayuda = models.CharField(max_length=200, blank=True)
    orden_de_campo = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creador = models.ForeignKey('users.User', on_delete=models.SET_NULL,related_name='mantenimientos_doc_campo_creados',null=True)
    grupo_documento = models.ForeignKey('Mantenimiento_DOC_GRUPO', on_delete=models.SET_NULL, related_name='campos_grupo',null=True, blank=True)


def can_view_mantenimientos(user: User)-> bool:
    return tiene_acceso(user, 'MAN')

def can_CRUD_mantenimientos(user: User)-> bool:
    return tiene_acceso(user, 'MAN', nivel_min='2')