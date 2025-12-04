"""Formularios para creación y edición de entidades de la app Usuarios."""
from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Area, Departamento, Cargo, Trabajador
from datetime import date
from .models import Trabajador, ContactoEmergencia, CargaFamiliar

class TrabajadorCreateForm(forms.ModelForm):
    """Formulario de alta administrativa de `Trabajador`."""
    class Meta:
        model = Trabajador
        fields = [
            'user', 'rut', 'nombres', 'apellidos', 'sexo', 'fecha_ingreso',
            'area', 'departamento', 'cargo', 'telefono', 'direccion'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo usuarios que no estén ya vinculados a un Trabajador
        UserModel = get_user_model()
        self.fields['user'].queryset = UserModel.objects.filter(trabajador__isnull=True).order_by('username')

class TrabajadorPersonalForm(forms.ModelForm):
    """Formulario para que el propio trabajador edite datos personales."""
    class Meta:
        model = Trabajador
        fields = ['nombres', 'apellidos', 'sexo', 'rut', 'fecha_ingreso', 'telefono', 'direccion']

class ContactoEmergenciaForm(forms.ModelForm):
    """Formulario para contactos de emergencia."""
    class Meta:
        model = ContactoEmergencia
        fields = ['nombre', 'parentesco', 'telefono']

class CargaFamiliarForm(forms.ModelForm):
    """Formulario para cargas familiares (hijos, dependientes, etc.)."""
    class Meta:
        model = CargaFamiliar
        fields = ['nombre', 'parentesco', 'fecha_nacimiento']

# Formset para gestionar múltiples contactos con un mismo trabajador
ContactoFormSet = inlineformset_factory(
    Trabajador, ContactoEmergencia,
    form=ContactoEmergenciaForm, extra=1, can_delete=True
)


class UsuarioCreateForm(UserCreationForm):
    """Formulario de creación de usuario con estilos Bootstrap y email obligatorio."""
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            widget = self.fields[name].widget
            attrs = getattr(widget, 'attrs', {})
            attrs.update({'class': 'form-control'})
            widget.attrs = attrs

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        UserModel = get_user_model()
        if email and UserModel.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este email.')
        return email


class UsuarioSignupForm(UsuarioCreateForm):
    nombres = forms.CharField(max_length=120)
    apellidos = forms.CharField(max_length=120)
    sexo = forms.ChoiceField(choices=Trabajador._meta.get_field('sexo').choices)
    rut = forms.CharField(max_length=12, required=False)
    fecha_ingreso = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    area = forms.ModelChoiceField(queryset=Area.objects.all(), required=False)
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False)
    cargo = forms.ModelChoiceField(queryset=Cargo.objects.all(), required=False)

    class Meta(UsuarioCreateForm.Meta):
        fields = (
            'username', 'email', 'password1', 'password2',
            'nombres', 'apellidos', 'sexo', 'rut', 'fecha_ingreso',
            'area', 'departamento', 'cargo'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ['nombres','apellidos','sexo','rut','fecha_ingreso','area','departamento','cargo']:
            widget = self.fields[name].widget
            attrs = getattr(widget, 'attrs', {})
            attrs.update({'class': 'form-control'})
            widget.attrs = attrs

    def clean(self):
        cleaned = super().clean()
        area = cleaned.get('area')
        departamento = cleaned.get('departamento')
        if area and departamento and departamento.area_id != area.id:
            self.add_error('departamento', 'El departamento no pertenece al área seleccionada.')
        return cleaned

# Formset para gestionar múltiples cargas familiares
CargaFormSet = inlineformset_factory(
    Trabajador, CargaFamiliar,
    form=CargaFamiliarForm, extra=1, can_delete=True
)
