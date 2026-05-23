from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class PerfilUsuario(models.Model):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('operador', 'Operador'),
        ('consulta', 'Consulta'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='consulta')
    telefono_whatsapp = models.CharField(max_length=20, blank=True)
    notif_email = models.BooleanField(default=True)
    notif_whatsapp = models.BooleanField(default=False)
    dias_anticipacion = models.PositiveIntegerField(default=7)

    def __str__(self):
        return f"{self.usuario.get_full_name()} ({self.get_rol_display()})"

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"


class Propietario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cuit = models.CharField(max_length=13, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

    class Meta:
        verbose_name = "Propietario"
        verbose_name_plural = "Propietarios"
        ordering = ['apellido', 'nombre']


class Propiedad(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('alquilada', 'Alquilada'),
        ('mantenimiento', 'En Mantenimiento'),
    ]
    propietario = models.ForeignKey(Propietario, on_delete=models.PROTECT, related_name='propiedades')
    domicilio = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=200, blank=True)
    padron_catastral = models.CharField(max_length=50, blank=True, verbose_name="Padrón Catastral")
    padron_municipal = models.CharField(max_length=50, blank=True, verbose_name="Padrón Municipal")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    titulares = models.ManyToManyField(Propietario, through='TitularPropiedad', related_name='propiedades_como_titular')
    notas = models.TextField(blank=True)
    fecha_alta = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.domicilio

    class Meta:
        verbose_name = "Propiedad"
        verbose_name_plural = "Propiedades"
        ordering = ['domicilio']


class TitularPropiedad(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE)
    titular = models.ForeignKey(Propietario, on_delete=models.PROTECT)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    es_titular_principal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.titular} — {self.propiedad} ({self.porcentaje}%)"

    class Meta:
        verbose_name = "Titular de Propiedad"
        verbose_name_plural = "Titulares de Propiedades"
        unique_together = ('propiedad', 'titular')


class ServicioImpuesto(models.Model):
    TIPO_CHOICES = [
        ('servicio', 'Servicio'),
        ('impuesto', 'Impuesto'),
    ]
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    icono = models.CharField(max_length=50, blank=True, help_text="Clase de ícono FontAwesome")

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

    class Meta:
        verbose_name = "Servicio / Impuesto"
        verbose_name_plural = "Servicios e Impuestos"
        ordering = ['tipo', 'nombre']


class PropiedadServicio(models.Model):
    RESPONSABLE_CHOICES = [
        ('propietario', 'Propietario'),
        ('inquilino', 'Inquilino'),
    ]
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='servicios')
    servicio = models.ForeignKey(ServicioImpuesto, on_delete=models.PROTECT)
    numero_cuenta = models.CharField(max_length=100, blank=True, verbose_name="N° de Cuenta / Servicio")
    numero_medidor = models.CharField(max_length=100, blank=True, verbose_name="N° de Medidor")
    responsable_pago = models.CharField(max_length=20, choices=RESPONSABLE_CHOICES, default='propietario')
    activo = models.BooleanField(default=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.propiedad} — {self.servicio}"

    class Meta:
        verbose_name = "Servicio de Propiedad"
        verbose_name_plural = "Servicios de Propiedades"
        unique_together = ('propiedad', 'servicio')


class Inquilino(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni_cuit = models.CharField(max_length=13, blank=True, verbose_name="DNI / CUIT")
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

    class Meta:
        verbose_name = "Inquilino"
        verbose_name_plural = "Inquilinos"
        ordering = ['apellido', 'nombre']


class Contrato(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('vencido', 'Vencido'),
        ('rescindido', 'Rescindido'),
    ]
    MONEDA_CHOICES = [
        ('ARS', 'Pesos Argentinos'),
        ('USD', 'Dólares'),
    ]
    propiedad = models.ForeignKey(Propiedad, on_delete=models.PROTECT, related_name='contratos')
    inquilino = models.ForeignKey(Inquilino, on_delete=models.PROTECT, related_name='contratos')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    monto_alquiler = models.DecimalField(max_digits=12, decimal_places=2)
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default='ARS')
    ajuste_meses = models.PositiveIntegerField(default=3, verbose_name="Ajuste cada (meses)")
    porcentaje_ajuste = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.propiedad} — {self.inquilino} ({self.fecha_inicio} / {self.fecha_fin})"

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ['-fecha_inicio']


class Vencimiento(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('vencido', 'Vencido'),
    ]
    propiedad_servicio = models.ForeignKey(PropiedadServicio, on_delete=models.CASCADE, related_name='vencimientos')
    fecha_vencimiento = models.DateField()
    importe_estimado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    periodo = models.CharField(max_length=20, blank=True, help_text="Ej: Enero 2025")
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.propiedad_servicio} — {self.fecha_vencimiento}"

    def actualizar_estado(self):
        if self.estado == 'pendiente' and self.fecha_vencimiento < timezone.now().date():
            self.estado = 'vencido'
            self.save()

    class Meta:
        verbose_name = "Vencimiento"
        verbose_name_plural = "Vencimientos"
        ordering = ['fecha_vencimiento']


class Pago(models.Model):
    vencimiento = models.OneToOneField(Vencimiento, on_delete=models.CASCADE, related_name='pago')
    fecha_pago = models.DateField()
    importe_pagado = models.DecimalField(max_digits=12, decimal_places=2)
    numero_comprobante = models.CharField(max_length=100, blank=True, verbose_name="N° Comprobante")
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    observaciones = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.vencimiento.estado = 'pagado'
        self.vencimiento.save()

    def __str__(self):
        return f"Pago {self.vencimiento} — {self.fecha_pago}"

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha_pago']


class Documento(models.Model):
    TIPO_CHOICES = [
        ('escritura', 'Escritura'),
        ('plano', 'Plano'),
        ('seguro', 'Póliza de Seguro'),
        ('contrato', 'Contrato'),
        ('otro', 'Otro'),
    ]
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='otro')
    nombre = models.CharField(max_length=200)
    url_drive = models.URLField(blank=True)
    archivo = models.FileField(upload_to='documentos/', blank=True)
    notas = models.TextField(blank=True)
    subido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_carga = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.propiedad} — {self.nombre}"

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-fecha_carga']
