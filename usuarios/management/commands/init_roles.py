from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from usuarios.models import Trabajador

class Command(BaseCommand):
    help = "Inicializa grupos: Administrador, Jefe RR.HH., Trabajador"

    def handle(self, *args, **kwargs):
        grupos = {
            'Administrador': {'perms': Permission.objects.all()},
            'Jefe RR.HH.': {'perms': Permission.objects.filter(codename__in=[
                'view_trabajador', 'add_trabajador', 'change_trabajador',
                'view_area', 'add_area', 'change_area',
                'view_departamento', 'add_departamento', 'change_departamento',
                'view_cargo', 'add_cargo', 'change_cargo',
            ])},
            'Trabajador': {'perms': Permission.objects.filter(codename__in=[
                'view_trabajador',  # puede verse a sí mismo (luego restringimos en la vista)
                'view_area', 'view_departamento', 'view_cargo',
            ])},
        }
        for nombre, cfg in grupos.items():
            g, _ = Group.objects.get_or_create(name=nombre)
            g.permissions.set(cfg['perms'])
            self.stdout.write(self.style.SUCCESS(f'Grupo "{nombre}" inicializado'))