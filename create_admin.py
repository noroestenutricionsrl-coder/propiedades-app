import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'propiedades_app.settings')
django.setup()
from django.contrib.auth.models import User
from core.models import PerfilUsuario, ServicioImpuesto

if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'noroestenutricionsrl@gmail.com', 'Admin2025!')
    u.first_name = 'Daniela'
    u.save()
    PerfilUsuario.objects.create(usuario=u, rol='admin', dias_anticipacion=7)
    print('Usuario admin creado')
else:
    print('Ya existe')

servicios = [
    ('Luz (EDET)', 'servicio'),
    ('Gas (Gasnor)', 'servicio'),
    ('Agua (SIDET)', 'servicio'),
    ('Internet', 'servicio'),
    ('Expensas', 'servicio'),
    ('TGI - Tasa General de Inmuebles', 'impuesto'),
    ('Contribución de Mejoras', 'impuesto'),
    ('Rentas - DGR Tucumán', 'impuesto'),
    ('ABL Municipal', 'impuesto'),
]

for nombre, tipo in servicios:
    obj, created = ServicioImpuesto.objects.get_or_create(nombre=nombre, defaults={'tipo': tipo})
    if created:
        print(f'Servicio creado: {nombre}')