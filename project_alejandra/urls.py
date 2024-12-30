from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_alejandra.urls')),  # Conecta las URLs de mi_app
]
