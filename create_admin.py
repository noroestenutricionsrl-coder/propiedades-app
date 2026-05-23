import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'propiedades_app.settings')
django.setup()
from django.contrib.auth.models import User
from core.models import PerfilUsuario
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'noroestenutricionsrl@gmail.com', 'Admin2025!')
    u.first_name = 'Daniela'
    u.save()
    PerfilUsuario.objects.create(usuario=u, rol='admin', dias_anticipacion=7)
    print('Usuario admin creado')
else:
    print('Ya existe')
