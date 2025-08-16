from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('insumos/', views.supplies_view, name='insumos'),
    path('productos/', views.product_view, name='productos'),
    path('proveedores/', views.proveedor_view, name='proveedores'),
    path('proveedores/eliminar/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('compras/', views.compras_view, name='compras'),
    path('clientes/', views.cliente_view, name='clientes'),
    path('clientes/eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('manualistas/', views.manualista_view, name='manualistas'),
    path('manualistas/eliminar/<int:manualista_id>/', views.eliminar_manualista, name='eliminar_manualista'),
    path('produccion/', views.produccion_view, name='produccion'),
    path('produccion/guardar/', views.produccion_view, name='guardar_produccion'),
    path('produccion/calcular/', views.calcular_produccion, name='calcular_produccion'),
    path('seguimiento-produccion/', views.seguimiento_produccion_view, name='seguimiento_produccion'),
    path('ventas/', views.ventas_view, name='ventas'),
]
