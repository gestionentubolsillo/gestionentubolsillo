from django.core.management.base import BaseCommand
from servicios.models import Servicio
class Command(BaseCommand):
    help = "Migra datos sensibles de usuario a su versión encriptada"

    def handle(self, *args, **options):
        servicios = Servicio.objects.all()
        total = servicios.count()

        for i, servicio in enumerate(servicios,1):
            servicio.mail_de_contacto_enc = servicio.mail_de_contacto

            servicio.save()
            self.stdout.write(f'[{i}/{total}] servicio {servicio.nombre} migrado')

        self.stdout.write(self.style.SUCCESS('Migración completada'))