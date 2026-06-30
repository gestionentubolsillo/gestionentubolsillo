from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(PermisosModulo)
admin.site.register(Cuadrante)


class CuentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active']
    exclude = ['file_key_encription']

admin.site.register(Cuenta,CuentaAdmin)