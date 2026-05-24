from django.core.management.base import BaseCommand
from core.alertas import enviar_alertas


class Command(BaseCommand):
    help = 'Envía alertas de vencimientos por email'

    def handle(self, *args, **options):
        self.stdout.write('Enviando alertas...')
        enviar_alertas()
        self.stdout.write(self.style.SUCCESS('Alertas enviadas correctamente'))
