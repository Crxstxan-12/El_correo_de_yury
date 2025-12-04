from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import date
from .models import Trabajador, Area, Departamento, Cargo

# Modelo de usuario activo
User = get_user_model()
from .forms import (
    TrabajadorCreateForm, TrabajadorPersonalForm,
    ContactoFormSet, CargaFormSet, UsuarioCreateForm, UsuarioSignupForm
)

@login_required(login_url='usuarios:login')
def logout_view(request):
    """Cierra sesión y redirige al formulario de autenticación."""
    logout(request)
    return redirect('usuarios:login')

@login_required(login_url='usuarios:login')
def lista_usuarios(request):
    """Lista todos los usuarios del sistema"""
    # Solo Administrador o superusuario puede ver el listado de usuarios
    if not (request.user.is_superuser or _user_in_group(request.user, 'Administrador')):
        return redirect('usuarios:perfil')

    usuarios = User.objects.all()
    trabajadores = Trabajador.objects.all()
    can_create_users = request.user.is_superuser or _user_in_group(request.user, 'Administrador')
    context = {'usuarios': usuarios, 'trabajadores': trabajadores, 'can_create_users': can_create_users}
    return render(request, 'usuarios/lista_usuarios.html', context)

@login_required(login_url='usuarios:login')
def lista_trabajadores(request):
    """Listado con filtros, orden y paginación de `Trabajador`.

    Restringe acceso a perfiles RR.HH., Administrador o superusuario.
    Soporta búsqueda por nombre, RUT (si existe), área, cargo, depto y sexo.
    """
    # Solo RR.HH., Administrador o superusuario pueden ver el listado de trabajadores
    if not (request.user.is_superuser or _user_in_group(request.user, 'Jefe RR.HH.') or _user_in_group(request.user, 'Administrador')):
        return redirect('usuarios:perfil')

    trabajadores_qs = Trabajador.objects.select_related('area', 'departamento', 'cargo', 'user')

    # Parámetros GET
    q = request.GET.get('q', '').strip()
    rut = request.GET.get('rut', '').strip()
    area_id = request.GET.get('area', '').strip()
    cargo_id = request.GET.get('cargo', '').strip()
    depto_id = request.GET.get('depto', '').strip()
    order = request.GET.get('order', 'name_asc')
    page = request.GET.get('page', '1')
    sexo = request.GET.get('sexo', '').strip()

    # Detectar si el modelo tiene campo 'rut'
    has_rut = any(f.name == 'rut' for f in Trabajador._meta.get_fields())

    # Filtros
    if q:
        trabajadores_qs = trabajadores_qs.filter(
            Q(nombres__icontains=q) | Q(apellidos__icontains=q)
        )
    if has_rut and rut:
        trabajadores_qs = trabajadores_qs.filter(rut__icontains=rut)
    if area_id:
        trabajadores_qs = trabajadores_qs.filter(area_id=area_id)
    if cargo_id:
        trabajadores_qs = trabajadores_qs.filter(cargo_id=cargo_id)
    if depto_id:
        trabajadores_qs = trabajadores_qs.filter(departamento_id=depto_id)
    if sexo:
        trabajadores_qs = trabajadores_qs.filter(sexo=sexo)

    # Orden
    order_map = {
        'name_asc': ['apellidos', 'nombres'],
        'name_desc': ['-apellidos', '-nombres'],
        'date_asc': ['fecha_ingreso', 'apellidos', 'nombres'],
        'date_desc': ['-fecha_ingreso', 'apellidos', 'nombres'],
    }
    trabajadores_qs = trabajadores_qs.order_by(*order_map.get(order, ['apellidos', 'nombres']))

    # Conteos y paginación
    filtered_count = trabajadores_qs.count()
    # Paginación robusta: sanitiza el parámetro y usa get_page
    page_str = request.GET.get("page", "1")
    try:
        page_num = int(page_str)
    except (TypeError, ValueError):
        page_num = 1
    if page_num < 1:
        page_num = 1

    paginator = Paginator(trabajadores_qs, 10)
    page_obj = paginator.get_page(page_num)

    # Query base para paginación (sin 'page')
    qs_copy = request.GET.copy()
    qs_copy.pop('page', None)
    base_qs = qs_copy.urlencode()

    context = {
        'trabajadores': page_obj.object_list,
        'page_obj': page_obj,
        'filtered_count': filtered_count,
        'areas': Area.objects.all(),
        'cargos': Cargo.objects.all(),
        'departamentos': Departamento.objects.all(),
        'filters': {'q': q, 'rut': rut, 'area': area_id, 'cargo': cargo_id, 'depto': depto_id, 'order': order, 'sexo': sexo},
        'has_rut': has_rut,
        'base_qs': base_qs,
        'total_trabajadores': Trabajador.objects.count(),
        'total_areas': Area.objects.count(),
        'total_departamentos': Departamento.objects.count(),
        'total_cargos': Cargo.objects.count(),
    }
    return render(request, 'usuarios/lista_trabajadores.html', context)

@login_required(login_url='usuarios:login')
def dashboard(request):
    """Panel principal del sistema"""
    context = {
        'total_usuarios': User.objects.count(),
        'total_trabajadores': Trabajador.objects.count(),
        'total_departamentos': Departamento.objects.count(),
        'total_cargos': Cargo.objects.count(),
        'total_areas': Area.objects.count(),
        # Banderas para mostrar/ocultar acciones y menús
        'can_view_users': request.user.is_superuser or _user_in_group(request.user, 'Administrador'),
        'can_view_trabajadores': request.user.is_superuser or _user_in_group(request.user, 'Jefe RR.HH.') or _user_in_group(request.user, 'Administrador'),
        'can_create_trabajador': request.user.is_superuser or _user_in_group(request.user, 'Jefe RR.HH.'),
        'can_create_usuario': request.user.is_superuser or _user_in_group(request.user, 'Administrador'),
        'can_manage_catalog': request.user.is_superuser or _user_in_group(request.user, 'Administrador'),
    }
    return render(request, 'usuarios/Dashboard.html', context)

@login_required(login_url='usuarios:login')
def api_dashboard(request):
    """API de métricas del dashboard (JSON)."""
    data = {
        'total_usuarios': User.objects.count(),
        'total_trabajadores': Trabajador.objects.count(),
        'total_departamentos': Departamento.objects.count(),
        'total_cargos': Cargo.objects.count(),
        'total_areas': Area.objects.count(),
    }
    return JsonResponse(data)

@login_required(login_url='usuarios:login')
def api_trabajadores(request):
    """API simple de trabajadores para pruebas de integración."""
    trabajadores = [{'id': t.id, 'nombre': str(t)} for t in Trabajador.objects.all()]
    return JsonResponse({'trabajadores': trabajadores})

# función: root_redirect
from django.shortcuts import render, redirect

def root_redirect(request):
    """Redirige la raíz a `dashboard` si autenticado, si no a `login`."""
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')
    return redirect('usuarios:login')

@login_required(login_url='usuarios:login')
def lista_departamentos(request):
    """Listado de `Departamento` con filtros por nombre/área y orden."""
    dept_qs = Departamento.objects.select_related('area')

    q = request.GET.get('q', '').strip()
    area_id = request.GET.get('area', '').strip()
    order = request.GET.get('order', 'name_asc')

    if q:
        dept_qs = dept_qs.filter(nombre__icontains=q)
    if area_id:
        dept_qs = dept_qs.filter(area_id=area_id)

    order_map = {
        'name_asc': ['nombre'],
        'name_desc': ['-nombre'],
        'area_asc': ['area__nombre', 'nombre'],
        'area_desc': ['-area__nombre', 'nombre'],
    }
    dept_qs = dept_qs.order_by(*order_map.get(order, ['nombre']))

    page_str = request.GET.get('page', '1')
    try:
        page_num = int(page_str)
    except (TypeError, ValueError):
        page_num = 1
    if page_num < 1:
        page_num = 1

    paginator = Paginator(dept_qs, 10)
    page_obj = paginator.get_page(page_num)

    qs_copy = request.GET.copy()
    qs_copy.pop('page', None)
    base_qs = qs_copy.urlencode()

    context = {
        'departamentos': page_obj.object_list,
        'areas': Area.objects.all(),
        'page_obj': page_obj,
        'base_qs': base_qs,
        'filters': {'q': q, 'area': area_id, 'order': order},
        'total_departamentos': Departamento.objects.count(),
        'total_areas': Area.objects.count(),
    }
    return render(request, 'usuarios/lista_departamentos.html', context)

@login_required(login_url='usuarios:login')
def lista_cargos(request):
    """Gestión y listado de `Cargo` con filtros y edición inline."""
    from django.db.models import Count

    cargos_qs = Cargo.objects.all()

    # Permiso para crear catálogo (cargos)
    can_manage_catalog = request.user.is_superuser or _user_in_group(request.user, 'Administrador')

    form_message = None
    form_status = None
    if request.method == 'POST':
        if not can_manage_catalog:
            form_message = 'No tiene permisos para gestionar cargos.'
            form_status = 'error'
        else:
            action = request.POST.get('action', 'create')
            nombre = request.POST.get('nombre', '').strip()
            cargo_id = request.POST.get('id')

            if action == 'create':
                if not nombre:
                    form_message = 'El nombre del cargo es obligatorio.'
                    form_status = 'error'
                else:
                    obj, created = Cargo.objects.get_or_create(nombre=nombre)
                    form_message = (f'Cargo "{nombre}" creado correctamente.' if created
                                    else f'El cargo "{nombre}" ya existía.')
                    form_status = ('success' if created else 'info')

            elif action == 'update':
                try:
                    c = Cargo.objects.get(pk=cargo_id)
                    if not nombre:
                        form_message = 'El nombre del cargo es obligatorio.'
                        form_status = 'error'
                    elif Cargo.objects.filter(nombre=nombre).exclude(pk=c.pk).exists():
                        form_message = f'Ya existe un cargo con el nombre "{nombre}".'
                        form_status = 'error'
                    else:
                        c.nombre = nombre
                        c.save()
                        form_message = 'Cargo actualizado correctamente.'
                        form_status = 'success'
                except Cargo.DoesNotExist:
                    form_message = 'Cargo no encontrado.'
                    form_status = 'error'

            elif action == 'delete':
                try:
                    Cargo.objects.get(pk=cargo_id).delete()
                    form_message = 'Cargo eliminado.'
                    form_status = 'success'
                except Cargo.DoesNotExist:
                    form_message = 'Cargo no encontrado.'
                    form_status = 'error'
    # Filtros y orden
    q = request.GET.get('q', '').strip()
    order = request.GET.get('order', 'name_asc')

    if q:
        cargos_qs = cargos_qs.filter(nombre__icontains=q)

    order_map = {
        'name_asc': ['nombre'],
        'name_desc': ['-nombre'],
        'count_asc': ['num_trabajadores', 'nombre'],
        'count_desc': ['-num_trabajadores', 'nombre'],
    }

    # Annotate cantidad de trabajadores por cargo
    cargos_qs = cargos_qs.annotate(num_trabajadores=Count('trabajador'))

    cargos_qs = cargos_qs.order_by(*order_map.get(order, ['nombre']))

    # Paginación robusta
    page_str = request.GET.get('page', '1')
    try:
        page_num = int(page_str)
    except (TypeError, ValueError):
        page_num = 1
    if page_num < 1:
        page_num = 1

    paginator = Paginator(cargos_qs, 10)
    page_obj = paginator.get_page(page_num)

    # Query base para paginación
    qs_copy = request.GET.copy()
    qs_copy.pop('page', None)
    base_qs = qs_copy.urlencode()

    context = {
        'cargos': page_obj.object_list,
        'page_obj': page_obj,
        'base_qs': base_qs,
        'filters': {'q': q, 'order': order},
        'form_message': form_message,
        'form_status': form_status,
        'total_cargos': Cargo.objects.count(),
        'total_trabajadores': Trabajador.objects.count(),
        'can_manage_catalog': can_manage_catalog,
    }
    return render(request, 'usuarios/lista_cargos.html', context)

@login_required(login_url='usuarios:login')
def lista_areas(request):
    """Gestión y listado de `Area` con métricas (deptos y trabajadores)."""
    from django.db.models import Count

    # Permiso para crear catálogo (áreas)
    can_manage_catalog = request.user.is_superuser or _user_in_group(request.user, 'Administrador')

    form_message = None
    form_status = None
    if request.method == 'POST':
        if not can_manage_catalog:
            form_message = 'No tiene permisos para gestionar áreas.'
            form_status = 'error'
        else:
            action = request.POST.get('action', 'create')
            nombre = request.POST.get('nombre', '').strip()
            area_id = request.POST.get('id')

            if action == 'create':
                if not nombre:
                    form_message = 'El nombre del área es obligatorio.'
                    form_status = 'error'
                else:
                    obj, created = Area.objects.get_or_create(nombre=nombre)
                    form_message = (f'Área "{nombre}" creada correctamente.' if created
                                    else f'El área "{nombre}" ya existía.')
                    form_status = ('success' if created else 'info')

            elif action == 'update':
                try:
                    a = Area.objects.get(pk=area_id)
                    if not nombre:
                        form_message = 'El nombre del área es obligatorio.'
                        form_status = 'error'
                    elif Area.objects.filter(nombre=nombre).exclude(pk=a.pk).exists():
                        form_message = f'Ya existe un área con el nombre "{nombre}".'
                        form_status = 'error'
                    else:
                        a.nombre = nombre
                        a.save()
                        form_message = 'Área actualizada correctamente.'
                        form_status = 'success'
                except Area.DoesNotExist:
                    form_message = 'Área no encontrada.'
                    form_status = 'error'

            elif action == 'delete':
                try:
                    Area.objects.get(pk=area_id).delete()
                    form_message = 'Área eliminada.'
                    form_status = 'success'
                except Area.DoesNotExist:
                    form_message = 'Área no encontrada.'
                    form_status = 'error'
    areas_qs = Area.objects.all().annotate(
        num_departamentos=Count('departamentos'),
        num_trabajadores=Count('trabajador')
    )

    # Filtros y orden
    q = request.GET.get('q', '').strip()
    order = request.GET.get('order', 'name_asc')

    if q:
        areas_qs = areas_qs.filter(nombre__icontains=q)

    order_map = {
        'name_asc': ['nombre'],
        'name_desc': ['-nombre'],
        'dept_asc': ['num_departamentos', 'nombre'],
        'dept_desc': ['-num_departamentos', 'nombre'],
        'emp_asc': ['num_trabajadores', 'nombre'],
        'emp_desc': ['-num_trabajadores', 'nombre'],
    }
    areas_qs = areas_qs.order_by(*order_map.get(order, ['nombre']))

    # Paginación robusta
    page_str = request.GET.get('page', '1')
    try:
        page_num = int(page_str)
    except (TypeError, ValueError):
        page_num = 1
    if page_num < 1:
        page_num = 1

    paginator = Paginator(areas_qs, 10)
    page_obj = paginator.get_page(page_num)

    # Query base para paginación
    qs_copy = request.GET.copy()
    qs_copy.pop('page', None)
    base_qs = qs_copy.urlencode()

    context = {
        'areas': page_obj.object_list,
        'page_obj': page_obj,
        'base_qs': base_qs,
        'filters': {'q': q, 'order': order},
        'form_message': form_message,
        'form_status': form_status,
        'total_areas': Area.objects.count(),
        'can_manage_catalog': can_manage_catalog,
    }
    return render(request, 'usuarios/lista_areas.html', context)


@login_required(login_url='usuarios:login')
def perfil(request):
    """Edición del perfil del trabajador asociado al usuario activo."""
    # El trabajador solo edita su propio registro
    trabajador = getattr(request.user, 'trabajador', None)
    if not trabajador:
        # Si no hay vínculo, puedes redirigir o crear uno según reglas del negocio
        return redirect('usuarios:dashboard')

    if request.method == 'POST':
        form = TrabajadorPersonalForm(request.POST, instance=trabajador)
        contacto_fs = ContactoFormSet(request.POST, instance=trabajador, prefix='contacto')
        carga_fs = CargaFormSet(request.POST, instance=trabajador, prefix='carga')
        if form.is_valid() and contacto_fs.is_valid() and carga_fs.is_valid():
            form.save()
            contacto_fs.save()
            carga_fs.save()
            return render(request, 'usuarios/perfil.html', {
                'form': form, 'contacto_fs': contacto_fs, 'carga_fs': carga_fs,
                'message': 'Datos actualizados correctamente.', 'message_type': 'success',
                'can_view_trabajadores': (request.user.is_superuser or _user_in_group(request.user, 'Jefe RR.HH.') or _user_in_group(request.user, 'Administrador')),
                'can_view_users': (request.user.is_superuser or _user_in_group(request.user, 'Administrador')),
            })
    else:
        form = TrabajadorPersonalForm(instance=trabajador)
        contacto_fs = ContactoFormSet(instance=trabajador, prefix='contacto')
        carga_fs = CargaFormSet(instance=trabajador, prefix='carga')

    return render(request, 'usuarios/perfil.html', {
        'form': form, 'contacto_fs': contacto_fs, 'carga_fs': carga_fs,
        'can_view_trabajadores': (request.user.is_superuser or _user_in_group(request.user, 'Jefe RR.HH.') or _user_in_group(request.user, 'Administrador')),
        'can_view_users': (request.user.is_superuser or _user_in_group(request.user, 'Administrador')),
    })


def _user_in_group(user, name):
    return user.groups.filter(name=name).exists()

@login_required(login_url='usuarios:login')
def alta_trabajador(request):
    """Alta de un nuevo `Trabajador` con formsets de contactos y cargas."""
    # Permiso: superusuario o Jefe RR.HH.
    if not (request.user.is_superuser or _user_in_group(request.user, 'Jefe RR.HH.')):
        return redirect('usuarios:dashboard')

    if request.method == 'POST':
        form = TrabajadorCreateForm(request.POST)
        if form.is_valid():
            trabajador = form.save(commit=False)
            trabajador.save()
            # Guardar formsets ya con la instancia creada
            contacto_fs = ContactoFormSet(request.POST, instance=trabajador, prefix='contacto')
            carga_fs = CargaFormSet(request.POST, instance=trabajador, prefix='carga')
            if contacto_fs.is_valid() and carga_fs.is_valid():
                contacto_fs.save()
                carga_fs.save()
                return render(request, 'usuarios/alta_trabajador.html', {
                    'form': TrabajadorCreateForm(),  # limpio para nuevo registro
                    'contacto_fs': ContactoFormSet(prefix='contacto', instance=Trabajador()),
                    'carga_fs': CargaFormSet(prefix='carga', instance=Trabajador()),
                    'message': 'Trabajador registrado correctamente.',
                    'message_type': 'success'
                })
        # Si principal inválido, reconstruir formsets para mostrar errores
        contacto_fs = ContactoFormSet(request.POST, prefix='contacto', instance=Trabajador())
        carga_fs = CargaFormSet(request.POST, prefix='carga', instance=Trabajador())
        return render(request, 'usuarios/alta_trabajador.html', {
            'form': form, 'contacto_fs': contacto_fs, 'carga_fs': carga_fs
        })

    # GET: formularios vacíos
    form = TrabajadorCreateForm()
    # Para render, usamos una instancia vacía (no se guarda hasta POST)
    contacto_fs = ContactoFormSet(prefix='contacto', instance=Trabajador())
    carga_fs = CargaFormSet(prefix='carga', instance=Trabajador())
    return render(request, 'usuarios/alta_trabajador.html', {
        'form': form, 'contacto_fs': contacto_fs, 'carga_fs': carga_fs
    })

@login_required(login_url='usuarios:login')
def crear_usuario(request):
    """Crea `User` y asigna opcionalmente un `Group` existente."""
    # Permiso: superusuario, Administrador o Jefe RR.HH.
    if not (request.user.is_superuser or _user_in_group(request.user, 'Administrador') or _user_in_group(request.user, 'Jefe RR.HH.')):
        return redirect('usuarios:dashboard')

    message = None
    message_type = 'info'
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        group_name = request.POST.get('group', '').strip()
        if form.is_valid():
            user = form.save()
            if group_name:
                try:
                    group = Group.objects.get(name=group_name)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    pass
            # Crear Trabajador si no existe para permitir acceso a perfil
            if not hasattr(user, 'trabajador'):
                Trabajador.objects.create(
                    user=user,
                    nombres=user.username,
                    apellidos='Usuario',
                    sexo='O',
                    fecha_ingreso=date.today(),
                )
            message = 'Usuario creado correctamente.'
            message_type = 'success'
            form = UsuarioCreateForm()  # limpiar para siguiente alta
    else:
        form = UsuarioCreateForm()

    return render(request, 'usuarios/crear_usuario.html', {
        'form': form, 'message': message, 'message_type': message_type,
        'groups': Group.objects.all().order_by('name')
    })
def signup(request):
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')
    message = None
    message_type = 'info'
    if request.method == 'POST':
        form = UsuarioSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Asignar grupo Trabajador y crear registro Trabajador por defecto
            try:
                grp, _ = Group.objects.get_or_create(name='Trabajador')
                user.groups.add(grp)
            except Exception:
                pass
            if not hasattr(user, 'trabajador'):
                Trabajador.objects.create(
                    user=user,
                    nombres=form.cleaned_data.get('nombres') or user.username,
                    apellidos=form.cleaned_data.get('apellidos') or 'Usuario',
                    sexo=form.cleaned_data.get('sexo') or 'O',
                    rut=form.cleaned_data.get('rut') or None,
                    fecha_ingreso=form.cleaned_data.get('fecha_ingreso') or date.today(),
                    area=form.cleaned_data.get('area'),
                    departamento=form.cleaned_data.get('departamento'),
                    cargo=form.cleaned_data.get('cargo'),
                )
            auth_login(request, user)
            return redirect('usuarios:dashboard')
    else:
        form = UsuarioSignupForm()
    return render(request, 'usuarios/signup.html', {
        'form': form, 'message': message, 'message_type': message_type
    })
