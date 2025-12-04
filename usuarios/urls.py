"""Rutas de la app Usuarios: autenticación, catálogo y gestión."""
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

app_name = 'usuarios'


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('lista/', views.lista_usuarios, name='lista_usuarios'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.perfil, name='perfil'),
    path('trabajadores/', views.lista_trabajadores, name='lista_trabajadores'),
    path('trabajadores/nuevo/', views.alta_trabajador, name='alta_trabajador'),
    path('usuarios/nuevo/', views.crear_usuario, name='crear_usuario'),
    path('departamentos/', views.lista_departamentos, name='lista_departamentos'),
    path('cargos/', views.lista_cargos, name='lista_cargos'),
    path('areas/', views.lista_areas, name='lista_areas'),
    path('deshboard/', RedirectView.as_view(pattern_name='usuarios:dashboard', permanent=False)),
    path('api/dashboard/', views.api_dashboard, name='api_dashboard'),
    path('api/trabajadores/', views.api_trabajadores, name='api_trabajadores'),
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='usuarios/password_change_form.html'
    ), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='usuarios/password_change_done.html'
    ), name='password_change_done'),
]
