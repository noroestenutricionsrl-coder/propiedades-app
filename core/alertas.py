from datetime import date, timedelta
from django.contrib.auth.models import User
from .models import Vencimiento, PerfilUsuario
import os


def enviar_email_sendgrid(destinatario, asunto, contenido_html):
    """Envía un email usando SendGrid API."""
    import urllib.request
    import json
    
    api_key = os.environ.get('SENDGRID_API_KEY', '')
    if not api_key:
        print("SENDGRID_API_KEY no configurada")
        return False
    
    data = {
        "personalizations": [{"to": [{"email": destinatario}]}],
        "from": {"email": "noroestenutricionsrl@gmail.com", "name": "Gestión de Propiedades"},
        "subject": asunto,
        "content": [{"type": "text/html", "value": contenido_html}]
    }
    
    req = urllib.request.Request(
        "https://api.sendgrid.com/v3/mail/send",
        data=json.dumps(data).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status == 202
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False


def generar_html_alerta(vencimientos_proximos, vencimientos_vencidos):
    """Genera el HTML del email de alerta."""
    html = """
    <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: #1a5c3a; padding: 20px; text-align: center;">
        <h1 style="color: white; margin: 0;">Gestión de Propiedades</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0">Alertas de Vencimientos</p>
    </div>
    """
    
    if vencimientos_vencidos:
        html += """
        <div style="background: #fdecea; border-left: 4px solid #c0392b; padding: 15px; margin: 20px 0;">
        <h2 style="color: #c0392b; margin: 0 0 10px">⚠️ Vencimientos sin pagar</h2>
        <table style="width:100%; border-collapse: collapse;">
        <tr style="background:#f8f8f8"><th style="padding:8px;text-align:left">Propiedad</th>
        <th style="padding:8px;text-align:left">Servicio</th>
        <th style="padding:8px;text-align:left">Vencimiento</th>
        <th style="padding:8px;text-align:left">Importe</th></tr>
        """
        for v in vencimientos_vencidos:
            html += f"""
            <tr><td style="padding:8px">{v.propiedad_servicio.propiedad.domicilio}</td>
            <td style="padding:8px">{v.propiedad_servicio.servicio.nombre}</td>
            <td style="padding:8px">{v.fecha_vencimiento.strftime('%d/%m/%Y')}</td>
            <td style="padding:8px">${v.importe_estimado or '—'}</td></tr>
            """
        html += "</table></div>"
    
    if vencimientos_proximos:
        html += """
        <div style="background: #fef9e7; border-left: 4px solid #d4a017; padding: 15px; margin: 20px 0;">
        <h2 style="color: #d4a017; margin: 0 0 10px">📅 Próximos a vencer (7 días)</h2>
        <table style="width:100%; border-collapse: collapse;">
        <tr style="background:#f8f8f8"><th style="padding:8px;text-align:left">Propiedad</th>
        <th style="padding:8px;text-align:left">Servicio</th>
        <th style="padding:8px;text-align:left">Vencimiento</th>
        <th style="padding:8px;text-align:left">Importe</th></tr>
        """
        for v in vencimientos_proximos:
            html += f"""
            <tr><td style="padding:8px">{v.propiedad_servicio.propiedad.domicilio}</td>
            <td style="padding:8px">{v.propiedad_servicio.servicio.nombre}</td>
            <td style="padding:8px">{v.fecha_vencimiento.strftime('%d/%m/%Y')}</td>
            <td style="padding:8px">${v.importe_estimado or '—'}</td></tr>
            """
        html += "</table></div>"
    
    html += """
    <div style="text-align:center; padding: 20px; color: #888; font-size: 12px;">
        <a href="https://propiedades-app-aq4o.onrender.com" 
           style="background:#1a5c3a;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">
            Ver en la app
        </a>
        <p style="margin-top:15px">Gestión de Propiedades — Sistema de alertas automáticas</p>
    </div>
    </body></html>
    """
    return html


def enviar_alertas():
    """Función principal que envía alertas a todos los usuarios configurados."""
    from .models import PatenteVehiculo, SeguroVehiculo
    hoy = date.today()
    en_7_dias = hoy + timedelta(days=7)
    
    # Actualizar vencidos
    Vencimiento.objects.filter(
        estado='pendiente', fecha_vencimiento__lt=hoy
    ).update(estado='vencido')
    PatenteVehiculo.objects.filter(
        estado='pendiente', fecha_vencimiento__lt=hoy
    ).update(estado='vencido')
    
    proximos = list(Vencimiento.objects.filter(
        estado='pendiente',
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=en_7_dias
    ).select_related('propiedad_servicio__propiedad', 'propiedad_servicio__servicio'))
    
    vencidos = list(Vencimiento.objects.filter(
        estado='vencido'
    ).select_related('propiedad_servicio__propiedad', 'propiedad_servicio__servicio'))

    patentes_proximas = list(PatenteVehiculo.objects.filter(
        estado='pendiente',
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=en_7_dias
    ).select_related('vehiculo'))

    patentes_vencidas = list(PatenteVehiculo.objects.filter(
        estado='vencido'
    ).select_related('vehiculo'))

    seguros_proximos = list(SeguroVehiculo.objects.filter(
        activo=True,
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=en_7_dias
    ).select_related('vehiculo'))

    seguros_vencidos = list(SeguroVehiculo.objects.filter(
        activo=True,
        fecha_vencimiento__lt=hoy
    ).select_related('vehiculo'))
    
    if not proximos and not vencidos and not patentes_proximas and not patentes_vencidas and not seguros_proximos and not seguros_vencidos:
        print("No hay alertas para enviar")
        return
    
    # Generar secciones de vehículos para el email
    if patentes_vencidas:
        vencidos_html_extra = "<h3 style='color:#c0392b;margin-top:20px'>Patentes vencidas</h3><table style='width:100%;border-collapse:collapse'><tr style='background:#f8f8f8'><th style='padding:8px;text-align:left'>Vehículo</th><th style='padding:8px;text-align:left'>Período</th><th style='padding:8px;text-align:left'>Vencimiento</th></tr>"
        for p in patentes_vencidas:
            vencidos_html_extra += f"<tr><td style='padding:8px'>{p.vehiculo}</td><td style='padding:8px'>{p.periodo}</td><td style='padding:8px'>{p.fecha_vencimiento.strftime('%d/%m/%Y')}</td></tr>"
        vencidos_html_extra += "</table>"
    else:
        vencidos_html_extra = ""

    if seguros_vencidos:
        seguros_html_extra = "<h3 style='color:#c0392b;margin-top:20px'>Seguros vencidos</h3><table style='width:100%;border-collapse:collapse'><tr style='background:#f8f8f8'><th style='padding:8px;text-align:left'>Vehículo</th><th style='padding:8px;text-align:left'>Compañía</th><th style='padding:8px;text-align:left'>Vencimiento</th></tr>"
        for s in seguros_vencidos:
            seguros_html_extra += f"<tr><td style='padding:8px'>{s.vehiculo}</td><td style='padding:8px'>{s.compania}</td><td style='padding:8px'>{s.fecha_vencimiento.strftime('%d/%m/%Y')}</td></tr>"
        seguros_html_extra += "</table>"
    else:
        seguros_html_extra = ""

    # Enviar a todos los usuarios con email activado
    perfiles = PerfilUsuario.objects.filter(notif_email=True).select_related('usuario')
    
    for perfil in perfiles:
        if not perfil.usuario.email:
            continue
        
        html = generar_html_alerta(proximos, vencidos)
        asunto = f"Alertas de vencimientos — {hoy.strftime('%d/%m/%Y')}"
        
        resultado = enviar_email_sendgrid(perfil.usuario.email, asunto, html)
        if resultado:
            print(f"Email enviado a {perfil.usuario.email}")
        else:
            print(f"Error enviando a {perfil.usuario.email}")
