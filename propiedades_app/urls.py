from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('propietarios/', views.propietarios_lista, name='propietarios_lista'),
    path('propietarios/nuevo/', views.propietario_crear, name='propietario_crear'),
    path('propietarios/<int:pk>/editar/', views.propietario_editar, name='propietario_editar'),
    path('propiedades/', views.propiedades_lista, name='propiedades_lista'),
    path('propiedades/nueva/', views.propiedad_crear, name='propiedad_crear'),
    path('propiedades/<int:pk>/', views.propiedad_detalle, name='propiedad_detalle'),
    path('propiedades/<int:pk>/editar/', views.propiedad_editar, name='propiedad_editar'),
    path('propiedades/<int:propiedad_pk>/servicio/', views.servicio_agregar, name='servicio_agregar'),
    path('propiedades/<int:propiedad_pk>/titular/', views.titular_agregar, name='titular_agregar'),
    path('propiedades/<int:propiedad_pk>/vencimiento/', views.vencimiento_crear, name='vencimiento_crear_propiedad'),
    path('vencimientos/', views.vencimientos_lista, name='vencimientos_lista'),
    path('vencimientos/nuevo/', views.vencimiento_crear, name='vencimiento_crear'),
    path('vencimientos/<int:vencimiento_id>/pagar/', views.registrar_pago, name='registrar_pago'),
    path('servicios/', views.servicios_lista, name='servicios_lista'),
    path('servicios/nuevo/', views.servicio_crear, name='servicio_crear'),
    path('servicios/<int:pk>/editar/', views.servicio_editar, name='servicio_editar'),
    path('alertas/enviar/', views.enviar_alertas_view, name='enviar_alertas'),
]
path('alertas/enviar/', views.enviar_alertas_view, name='enviar_alertas'),