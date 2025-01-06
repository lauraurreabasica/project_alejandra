from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_alejandra.urls')),  # Redirige las rutas raíz a app_alejandra
]
