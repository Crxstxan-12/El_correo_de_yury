from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Ejecuta en orden: migrate, seed_users, seed_rrhh, seed_demo_org y seed_cargas"

    def add_arguments(self, parser):
        parser.add_argument('--per-worker', type=int, default=2)
        parser.add_argument('--wipe-cargas', action='store_true', default=False)

    def handle(self, *args, **opts):
        call_command('migrate')
        call_command('seed_users')
        call_command('seed_rrhh')
        call_command('seed_demo_org')
        call_command('seed_cargas', per_worker=opts['per_worker'], wipe=opts['wipe_cargas'])
        self.stdout.write(self.style.SUCCESS('Seed completo ejecutado'))

