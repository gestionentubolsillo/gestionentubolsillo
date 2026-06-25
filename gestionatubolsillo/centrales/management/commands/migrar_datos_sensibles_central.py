from django.core.management.base import BaseCommand
from centrales.models import Central
class Command(BaseCommand):
    help = "Migra datos sensibles de usuario a su versión encriptada"

    def handle(self, *args, **options):
        centrales = Central.objects.all()
        total = centrales.count()

        for i, central in enumerate(centrales,1):
            central.telefono_enc = central.telefono
            central.mail_enc = central.mail

            central.save()
            self.stdout.write(f'[{i}/{total}] central {central.nombre} migrado')

        self.stdout.write(self.style.SUCCESS('Migración completada'))