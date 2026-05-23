from django.contrib import admin
from .models import *

admin.site.site_header = "Administración de Propiedades"
admin.site.site_title = "Propiedades"
admin.site.index_title = "Panel de Administración"

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'rol', 'notif_email', 'notif_whatsapp', 'dias_anticipacion']

@admin.register(Propietario)
class PropietarioAdmin(admin.ModelAdmin):
    list_display = ['apellido', 'nombre', 'cuit', 'email', 'telefono']
    search_fields = ['apellido', 'nombre', 'cuit']

class TitularPropiedadInline(admin.TabularInline):
    model = TitularPropiedad
    extra = 1

class PropiedadServicioInline(admin.TabularInline):
    model = PropiedadServicio
    extra = 1

@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    list_display = ['domicilio', 'propietario', 'estado', 'padron_catastral', 'padron_municipal']
    list_filter = ['estado', 'propietario']
    search_fields = ['domicilio', 'padron_catastral', 'padron_municipal']
    inlines = [TitularPropiedadInline, PropiedadServicioInline]

@admin.register(ServicioImpuesto)
class ServicioImpuestoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo']
    list_filter = ['tipo']

@admin.register(Inquilino)
class InquilinoAdmin(admin.ModelAdmin):
    list_display = ['apellido', 'nombre', 'dni_cuit', 'email', 'telefono']

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ['propiedad', 'inquilino', 'fecha_inicio', 'fecha_fin', 'monto_alquiler', 'moneda', 'estado']
    list_filter = ['estado', 'moneda']

@admin.register(Vencimiento)
class VencimientoAdmin(admin.ModelAdmin):
    list_display = ['propiedad_servicio', 'periodo', 'fecha_vencimiento', 'importe_estimado', 'estado']
    list_filter = ['estado']
    date_hierarchy = 'fecha_vencimiento'

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['vencimiento', 'fecha_pago', 'importe_pagado', 'numero_comprobante', 'registrado_por']
    date_hierarchy = 'fecha_pago'

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['propiedad', 'tipo', 'nombre', 'fecha_carga']
