from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('propiedades/', views.propiedades_lista, name='propiedades_lista'),
    path('propiedades/<int:pk>/', views.propiedad_detalle, name='propiedad_detalle'),
    path('vencimientos/', views.vencimientos_lista, name='vencimientos_lista'),
    path('vencimientos/<int:vencimiento_id>/pagar/', views.registrar_pago, name='registrar_pago'),
]
