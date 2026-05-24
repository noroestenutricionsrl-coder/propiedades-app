from django import forms
from .models import (
    Propiedad, Propietario, TitularPropiedad,
    ServicioImpuesto, PropiedadServicio,
    Vencimiento, Inquilino, Contrato
)


class PropietarioForm(forms.ModelForm):
    class Meta:
        model = Propietario
        fields = ['nombre', 'apellido', 'cuit', 'email', 'telefono', 'notas']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'cuit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '20-12345678-9'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+54 381 000-0000'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PropiedadForm(forms.ModelForm):
    class Meta:
        model = Propiedad
        fields = ['propietario', 'domicilio', 'descripcion', 'padron_catastral', 'padron_municipal', 'estado', 'notas']
        widgets = {
            'propietario': forms.Select(attrs={'class': 'form-control'}),
            'domicilio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'San Martín 450, Tucumán'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PH, local, departamento...'}),
            'padron_catastral': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Padrón catastral'}),
            'padron_municipal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Padrón municipal'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TitularPropiedadForm(forms.ModelForm):
    class Meta:
        model = TitularPropiedad
        fields = ['titular', 'porcentaje', 'es_titular_principal']
        widgets = {
            'titular': forms.Select(attrs={'class': 'form-control'}),
            'porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'es_titular_principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PropiedadServicioForm(forms.ModelForm):
    class Meta:
        model = PropiedadServicio
        fields = ['servicio', 'numero_cuenta', 'numero_medidor', 'responsable_pago', 'activo', 'notas']
        widgets = {
            'servicio': forms.Select(attrs={'class': 'form-control'}),
            'numero_cuenta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N° de cuenta o servicio'}),
            'numero_medidor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N° de medidor'}),
            'responsable_pago': forms.Select(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class VencimientoForm(forms.ModelForm):
    class Meta:
        model = Vencimiento
        fields = ['propiedad_servicio', 'fecha_vencimiento', 'importe_estimado', 'periodo', 'notas']
        widgets = {
            'propiedad_servicio': forms.Select(attrs={'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'importe_estimado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'periodo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Mayo 2025'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, propiedad=None, **kwargs):
        super().__init__(*args, **kwargs)
        if propiedad:
            self.fields['propiedad_servicio'].queryset = PropiedadServicio.objects.filter(
                propiedad=propiedad, activo=True
            ).select_related('servicio')


class InquilinoForm(forms.ModelForm):
    class Meta:
        model = Inquilino
        fields = ['nombre', 'apellido', 'dni_cuit', 'email', 'telefono', 'notas']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'dni_cuit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI o CUIT'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ['inquilino', 'fecha_inicio', 'fecha_fin', 'monto_alquiler', 'moneda', 'ajuste_meses', 'porcentaje_ajuste', 'estado', 'notas']
        widgets = {
            'inquilino': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'monto_alquiler': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-control'}),
            'ajuste_meses': forms.NumberInput(attrs={'class': 'form-control'}),
            'porcentaje_ajuste': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
class ServicioImpuestoForm(forms.ModelForm):
    class Meta:
        model = ServicioImpuesto
        fields = ['nombre', 'tipo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Luz (EDET)'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
        }
