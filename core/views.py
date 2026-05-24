from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from datetime import date, timedelta
from .models import *
import json


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        error = "Usuario o contraseña incorrectos."
    return render(request, 'core/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    hoy = date.today()
    en_7_dias = hoy + timedelta(days=7)
    
    # Actualizar estados vencidos
    Vencimiento.objects.filter(
        estado='pendiente', fecha_vencimiento__lt=hoy
    ).update(estado='vencido')

    proximos = Vencimiento.objects.filter(
        estado='pendiente',
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=en_7_dias
    ).select_related('propiedad_servicio__propiedad', 'propiedad_servicio__servicio').order_by('fecha_vencimiento')

    vencidos = Vencimiento.objects.filter(
        estado='vencido'
    ).select_related('propiedad_servicio__propiedad', 'propiedad_servicio__servicio').order_by('fecha_vencimiento')[:10]

    # Vencimientos del mes actual
    mes_actual = Vencimiento.objects.filter(
        fecha_vencimiento__year=hoy.year,
        fecha_vencimiento__month=hoy.month
    ).select_related('propiedad_servicio__propiedad', 'propiedad_servicio__servicio').order_by('fecha_vencimiento')

    stats = {
        'total_propiedades': Propiedad.objects.count(),
        'propiedades_alquiladas': Propiedad.objects.filter(estado='alquilada').count(),
        'vencimientos_proximos': proximos.count(),
        'vencimientos_vencidos': Vencimiento.objects.filter(estado='vencido').count(),
        'pagos_mes': Pago.objects.filter(
            fecha_pago__year=hoy.year,
            fecha_pago__month=hoy.month
        ).count(),
    }

    return render(request, 'core/dashboard.html', {
        'proximos': proximos,
        'vencidos': vencidos,
        'mes_actual': mes_actual,
        'stats': stats,
        'hoy': hoy,
        'mes_nombre': hoy.strftime('%B %Y').capitalize(),
    })


@login_required
def propiedades_lista(request):
    propiedades = Propiedad.objects.select_related('propietario').prefetch_related('titulares').all()
    estado = request.GET.get('estado', '')
    if estado:
        propiedades = propiedades.filter(estado=estado)
    busqueda = request.GET.get('q', '')
    if busqueda:
        propiedades = propiedades.filter(
            Q(domicilio__icontains=busqueda) |
            Q(padron_catastral__icontains=busqueda) |
            Q(padron_municipal__icontains=busqueda)
        )
    return render(request, 'core/propiedades_lista.html', {
        'propiedades': propiedades,
        'estado_filtro': estado,
        'busqueda': busqueda,
    })


@login_required
def propiedad_detalle(request, pk):
    propiedad = get_object_or_404(Propiedad, pk=pk)
    servicios = propiedad.servicios.filter(activo=True).select_related('servicio')
    contratos = propiedad.contratos.all().select_related('inquilino').order_by('-fecha_inicio')
    documentos = propiedad.documentos.all()
    
    # Vencimientos recientes y próximos
    hoy = date.today()
    vencimientos = Vencimiento.objects.filter(
        propiedad_servicio__propiedad=propiedad
    ).select_related('propiedad_servicio__servicio').order_by('-fecha_vencimiento')[:20]

    return render(request, 'core/propiedad_detalle.html', {
        'propiedad': propiedad,
        'servicios': servicios,
        'contratos': contratos,
        'documentos': documentos,
        'vencimientos': vencimientos,
        'hoy': hoy,
    })


@login_required
def vencimientos_lista(request):
    hoy = date.today()
    mes = int(request.GET.get('mes', hoy.month))
    anio = int(request.GET.get('anio', hoy.year))
    estado = request.GET.get('estado', '')
    propiedad_id = request.GET.get('propiedad', '')

    vencimientos = Vencimiento.objects.select_related(
        'propiedad_servicio__propiedad',
        'propiedad_servicio__servicio'
    ).filter(
        fecha_vencimiento__year=anio,
        fecha_vencimiento__month=mes
    )

    if estado:
        vencimientos = vencimientos.filter(estado=estado)
    if propiedad_id:
        vencimientos = vencimientos.filter(propiedad_servicio__propiedad_id=propiedad_id)

    vencimientos = vencimientos.order_by('fecha_vencimiento')
    propiedades = Propiedad.objects.all()

    return render(request, 'core/vencimientos_lista.html', {
        'vencimientos': vencimientos,
        'mes': mes,
        'anio': anio,
        'estado_filtro': estado,
        'propiedades': propiedades,
        'propiedad_filtro': propiedad_id,
        'meses': [(i, date(2000, i, 1).strftime('%B').capitalize()) for i in range(1, 13)],
    })


@login_required
def registrar_pago(request, vencimiento_id):
    vencimiento = get_object_or_404(Vencimiento, pk=vencimiento_id)
    perfil = getattr(request.user, 'perfil', None)
    if perfil and perfil.rol == 'consulta':
        return redirect('vencimientos_lista')

    if request.method == 'POST':
        fecha_pago = request.POST.get('fecha_pago')
        importe = request.POST.get('importe_pagado')
        comprobante = request.POST.get('numero_comprobante', '')
        obs = request.POST.get('observaciones', '')
        Pago.objects.update_or_create(
            vencimiento=vencimiento,
            defaults={
                'fecha_pago': fecha_pago,
                'importe_pagado': importe,
                'numero_comprobante': comprobante,
                'observaciones': obs,
                'registrado_por': request.user,
            }
        )
        return redirect(request.POST.get('next', 'vencimientos_lista'))

    return render(request, 'core/registrar_pago.html', {
        'vencimiento': vencimiento,
        'hoy': date.today().isoformat(),
    })


# ============ PROPIETARIOS ============

@login_required
def propietarios_lista(request):
    propietarios = Propietario.objects.all()
    return render(request, 'core/propietarios_lista.html', {'propietarios': propietarios})


@login_required
def propietario_crear(request):
    from .forms import PropietarioForm
    if request.user.perfil.rol == 'consulta':
        return redirect('propietarios_lista')
    if request.method == 'POST':
        form = PropietarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('propietarios_lista')
    else:
        form = PropietarioForm()
    return render(request, 'core/form_generico.html', {
        'form': form, 'titulo': 'Nuevo Propietario', 'volver': 'propietarios_lista'
    })


@login_required
def propietario_editar(request, pk):
    from .forms import PropietarioForm
    propietario = get_object_or_404(Propietario, pk=pk)
    if request.user.perfil.rol == 'consulta':
        return redirect('propietarios_lista')
    if request.method == 'POST':
        form = PropietarioForm(request.POST, instance=propietario)
        if form.is_valid():
            form.save()
            return redirect('propietarios_lista')
    else:
        form = PropietarioForm(instance=propietario)
    return render(request, 'core/form_generico.html', {
        'form': form, 'titulo': f'Editar — {propietario}', 'volver': 'propietarios_lista'
    })


# ============ PROPIEDADES ============

@login_required
def propiedad_crear(request):
    from .forms import PropiedadForm
    if request.user.perfil.rol == 'consulta':
        return redirect('propiedades_lista')
    if request.method == 'POST':
        form = PropiedadForm(request.POST)
        if form.is_valid():
            propiedad = form.save()
            return redirect('propiedad_detalle', pk=propiedad.pk)
    else:
        form = PropiedadForm()
    return render(request, 'core/form_generico.html', {
        'form': form, 'titulo': 'Nueva Propiedad', 'volver': 'propiedades_lista'
    })


@login_required
def propiedad_editar(request, pk):
    from .forms import PropiedadForm
    propiedad = get_object_or_404(Propiedad, pk=pk)
    if request.user.perfil.rol == 'consulta':
        return redirect('propiedad_detalle', pk=pk)
    if request.method == 'POST':
        form = PropiedadForm(request.POST, instance=propiedad)
        if form.is_valid():
            form.save()
            return redirect('propiedad_detalle', pk=propiedad.pk)
    else:
        form = PropiedadForm(instance=propiedad)
    return render(request, 'core/form_generico.html', {
        'form': form, 'titulo': f'Editar — {propiedad.domicilio}', 'volver': 'propiedades_lista'
    })


# ============ SERVICIOS ============

@login_required
def servicio_agregar(request, propiedad_pk):
    from .forms import PropiedadServicioForm
    propiedad = get_object_or_404(Propiedad, pk=propiedad_pk)
    if request.user.perfil.rol == 'consulta':
        return redirect('propiedad_detalle', pk=propiedad_pk)
    if request.method == 'POST':
        form = PropiedadServicioForm(request.POST)
        if form.is_valid():
            ps = form.save(commit=False)
            ps.propiedad = propiedad
            ps.save()
            return redirect('propiedad_detalle', pk=propiedad_pk)
    else:
        form = PropiedadServicioForm()
    return render(request, 'core/form_generico.html', {
        'form': form,
        'titulo': f'Agregar Servicio — {propiedad.domicilio}',
        'volver': 'propiedad_detalle',
        'volver_pk': propiedad_pk,
    })


# ============ VENCIMIENTOS ============

@login_required
def vencimiento_crear(request, propiedad_pk=None):
    from .forms import VencimientoForm
    if request.user.perfil.rol == 'consulta':
        return redirect('vencimientos_lista')
    propiedad = get_object_or_404(Propiedad, pk=propiedad_pk) if propiedad_pk else None
    if request.method == 'POST':
        form = VencimientoForm(request.POST, propiedad=propiedad)
        if form.is_valid():
            form.save()
            if propiedad:
                return redirect('propiedad_detalle', pk=propiedad_pk)
            return redirect('vencimientos_lista')
    else:
        form = VencimientoForm(propiedad=propiedad)
    return render(request, 'core/form_generico.html', {
        'form': form,
        'titulo': 'Nuevo Vencimiento',
        'volver': 'propiedad_detalle' if propiedad else 'vencimientos_lista',
        'volver_pk': propiedad_pk,
    })


# ============ TITULARES ============

@login_required
def titular_agregar(request, propiedad_pk):
    from .forms import TitularPropiedadForm
    propiedad = get_object_or_404(Propiedad, pk=propiedad_pk)
    if request.user.perfil.rol == 'consulta':
        return redirect('propiedad_detalle', pk=propiedad_pk)
    if request.method == 'POST':
        form = TitularPropiedadForm(request.POST)
        if form.is_valid():
            tp = form.save(commit=False)
            tp.propiedad = propiedad
            tp.save()
            return redirect('propiedad_detalle', pk=propiedad_pk)
    else:
        form = TitularPropiedadForm()
    return render(request, 'core/form_generico.html', {
        'form': form,
        'titulo': f'Agregar Titular — {propiedad.domicilio}',
        'volver': 'propiedad_detalle',
        'volver_pk': propiedad_pk,
    })
# ============ SERVICIOS MAESTRO ============

@login_required
def servicios_lista(request):
    servicios = ServicioImpuesto.objects.all().order_by('tipo', 'nombre')
    return render(request, 'core/servicios_lista.html', {'servicios': servicios})


@login_required
def servicio_crear(request):
    from .forms import ServicioImpuestoForm
    if request.user.perfil.rol != 'admin':
        return redirect('servicios_lista')
    if request.method == 'POST':
        form = ServicioImpuestoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('servicios_lista')
    else:
        form = ServicioImpuestoForm()
    return render(request, 'core/form_generico.html', {
        'form': form, 'titulo': 'Nuevo Servicio / Impuesto', 'volver': 'servicios_lista'
    })


@login_required
def servicio_editar(request, pk):
    from .forms import ServicioImpuestoForm
    servicio = get_object_or_404(ServicioImpuesto, pk=pk)
    if request.user.perfil.rol != 'admin':
        return redirect('servicios_lista')
    if request.method == 'POST':
        form = ServicioImpuestoForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect('servicios_lista')
    else:
        form = ServicioImpuestoForm(instance=servicio)
    return render(request, 'core/form_generico.html', {
        'form': form, 'titulo': f'Editar — {servicio.nombre}', 'volver': 'servicios_lista'
    })
