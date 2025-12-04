from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import random

class Command(BaseCommand):
    help = 'Crea grupos y usuarios de prueba con opciones de ampliación'

    def add_arguments(self, parser):
        parser.add_argument('--groups', nargs='*', default=['admin','manager','developer','viewer','support','sales','hr'])
        parser.add_argument('--create-base', action='store_true', default=True)
        parser.add_argument('--no-base', action='store_false', dest='create_base')
        parser.add_argument('--extra', type=int, default=10)
        parser.add_argument('--prefix', type=str, default='user')
        parser.add_argument('--password', type=str, default='pass1234')
        parser.add_argument('--update-password', action='store_true', default=False)
        parser.add_argument('--staff-groups', nargs='*', default=['admin','manager'])
        parser.add_argument('--superuser', type=str, default='admin_user')

    def handle(self, *args, **options):
        groups = options['groups']
        create_base = options['create_base']
        extra = options['extra']
        prefix = options['prefix']
        password = options['password']
        update_password = options['update_password']
        staff_groups = set(options['staff_groups'])
        superuser_username = options['superuser']

        # Crear grupos
        for name in groups:
            Group.objects.get_or_create(name=name)

        # Base de usuarios conocida
        if create_base:
            base_users = [
                ('admin_user','admin@example.com','adminpass','admin'),
                ('manager_user','manager@example.com','managerpass','manager'),
                ('dev_user','dev@example.com','devpass','developer'),
                ('viewer_user','viewer@example.com','viewerpass','viewer'),
            ]
            User = get_user_model()
            for username,email,base_pwd,group_name in base_users:
                u = User.objects.filter(username=username).first()
                if not u:
                    u = User.objects.create_user(username=username, email=email, password=base_pwd)
                elif update_password:
                    u.set_password(base_pwd)
                grp = Group.objects.get(name=group_name)
                u.groups.set([grp])
                u.is_staff = (group_name in staff_groups)
                u.is_superuser = (username == superuser_username)
                u.save()
                self.stdout.write(self.style.SUCCESS(f'Usuario {username} listo en grupo {group_name}'))

        # Usuarios extra distribuidos entre grupos
        User = get_user_model()
        for i in range(1, extra + 1):
            gname = random.choice(groups)
            username = f"{prefix}_{gname}_{i}"
            email = f"{username}@example.com"
            u = User.objects.filter(username=username).first()
            if not u:
                u = User.objects.create_user(username=username, email=email, password=password)
            elif update_password:
                u.set_password(password)
            grp = Group.objects.get(name=gname)
            u.groups.set([grp])
            u.is_staff = (gname in staff_groups)
            # No marcar superuser para extras
            u.save()
        self.stdout.write(self.style.SUCCESS(f'Usuarios extra: {extra} creados/actualizados con prefijo {prefix}'))
        self.stdout.write(self.style.SUCCESS('Grupos y usuarios de prueba listos'))
