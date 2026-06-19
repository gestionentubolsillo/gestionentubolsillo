from django.db.models.signals import post_save
from django.dispatch import receiver
from servicios.models import Servicio
from .models import Parte_Trabajo

@receiver(post_save, sender=Servicio)
def recalcular_partes_servicio(sender, instance, **kwargs):
    partes = Parte_Trabajo.objects.filter(servicio=instance)
    for parte in partes:
        parte.horas_calculadas = parte._calcular_horas()
    Parte_Trabajo.objects.bulk_update(partes, ['horas_calculadas'])
    