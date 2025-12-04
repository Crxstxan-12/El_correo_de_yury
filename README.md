[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=21587129)
Cristian Cifuentes, Cristobal Hernandez

# El Correo de Yury — Gestión de Trabajadores
Aplicación web para la gestión de trabajadores con autenticación, perfil personal, listado filtrable y administración de catálogos (Áreas, Departamentos, Cargos). Backend en Django con vistas HTML y preparado para API REST (DRF). Base de datos MySQL en producción.

## Arquitectura
- Backend: Django 5, preparado para Django REST Framework.
- Frontend: Plantillas HTML/CSS/JS (con Bootstrap 5), opcional React consumiendo la API.
- Base de datos: MySQL en producción.
- Comunicación: HTTPS en producción.

## Requisitos
  Python 3.10+
  Paquetes:
  Django 5.2.8
  djangorestframework 3.15.2
  django-filter 24.2
  django-cors-headers 4.4.0
  mysqlclient 2.2.4 (solo si usarás MySQL)
  python-dotenv 1.0.1
--pip install -r requirements.txt
Instalacion de dependencias


Crea superusuario:
python manage.py createsuperuser  

Grupos recomendados:
- `Administrador`
- `Jefe RR.HH.`

(Agrega usuarios a estos grupos desde `/admin/` para activar permisos)

## Ejecutar
Servidor de desarrollo:
python manage.py runserver

## Permisos y Roles
- Trabajador:
  - Edita datos personales, contactos de emergencia y cargas familiares
  - Ve datos laborales en modo lectura
- Jefe RR.HH.:
  - Alta y gestión de trabajadores, filtros en el listado
- Administrador:
  - Gestión de usuarios y catálogos, acceso total

  ## Seguridad (producción)
- Cookies seguras: `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- HSTS: `SECURE_HSTS_SECONDS`
- Contraseñas: `PBKDF2` por defecto (opcional `bcrypt` en `PASSWORD_HASHERS`)
- CSRF activo en formularios, nunca interpolar SQL manualmente


## API REST (DRF) — preparación
EndPoints previstos (cuando se activen los ViewSets):
- `GET/POST /api/trabajadores/`
- `GET/PUT/PATCH/DELETE /api/trabajadores/{id}/`
- `GET /api/areas/`, `GET /api/departamentos/`, `GET /api/cargos/`
- Filtros: `sexo`, `area`, `departamento`, `cargo`, `rut`, `q`, `order`

Habilitar CORS si usas React:
- `django-cors-headers` instalado
- `CORS_ALLOWED_ORIGINS` en `settings.py` con tu dominio React
- `CORS_ALLOW_CREDENTIALS = True`

## Desarrollo Rápido
- Migraciones y servidor: `migrate` → `runserver`
- Acceso a admin: `/admin/` (usa tu superusuario)
- Alta RR.HH.: asigna usuario al grupo `Jefe RR.HH.`
- Pruebas básicas:
  - Login con usuario válido/ inválido
  - Perfil: editar datos personales; ver datos laborales en lectura
  - Listado: filtros por sexo/cargo/área/departamento (RR.HH./Admin)


## Estructura Relevante
- `usuarios/views.py` — vistas de dashboard, perfil, listados y catálogos
- `usuarios/models.py` — `Trabajador`, `Area`, `Departamento`, `Cargo`
- `usuarios/forms.py` — formularios y formsets
- `usuarios/templates/usuarios/*` — plantillas HTML
- `usuarios/urls.py` — rutas de la app
- `el_correo/urls.py` — enrutado del proyecto

## Comandos de Management
- `init_roles`: Inicializa grupos base y permisos (Administrador, Jefe RR.HH., Trabajador). Ver `usuarios/management/commands/init_roles.py:6`.
- `seed_users`: Crea/actualiza usuarios de prueba y distribuye en grupos. Soporta `--groups`, `--extra`, `--prefix`, `--password`, `--update-password`, `--staff-groups`, `--superuser`. Ver `usuarios/management/commands/seed_users.py:7`.
- `seed_rrhh`: Asegura roles, crea usuarios clave (admin, leo), catálogos RR.HH. y vincula `Trabajador`. Ver `usuarios/management/commands/seed_rrhh.py:8`.
- `seed_demo_org`: Crea Áreas, Departamentos, Cargos y vincula usuarios de prueba a `Trabajador` con datos demo. Ver `usuarios/management/commands/seed_demo_org.py:7`.
- `seed_cargas`: Genera cargas familiares de prueba para cada `Trabajador`. Flags: `--per-worker`, `--min`, `--wipe`, `--max-age`, `--min-age`. Ver `usuarios/management/commands/seed_cargas.py:7`.
- `seed_all`: Ejecuta en orden `migrate`, `seed_users`, `seed_rrhh`, `seed_demo_org` y `seed_cargas`. Ver `usuarios/management/commands/seed_all.py:5`.
- `bootstrap_demo`: Ejecuta migraciones y semillas mínimas, y sanea `Trabajador` completando campos faltantes como `rut` y `fecha_ingreso`. Ver `usuarios/management/commands/bootstrap_demo.py:9`.

### Uso rápido
- `python manage.py init_roles`
- `python manage.py seed_users --extra 20 --prefix demo --update-password`
- `python manage.py seed_rrhh`
- `python manage.py seed_demo_org`
- `python manage.py seed_cargas --per-worker 3 --wipe`
- `python manage.py seed_all --per-worker 2`
- `python manage.py bootstrap_demo`
