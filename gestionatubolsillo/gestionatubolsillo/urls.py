"""
URL configuration for gestionatubolsillo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('', include('users.urls')),
    path('', include('clientes.urls')),
    path('', include('empresas.urls')),
    path('', include('partes.urls')),
    path('', include('servicios.urls')),
    path('', include('tareas.urls')),
    path('', include('almacen.urls')),
    path('', include('backoffice.urls')),
    path('', include('authentication.urls')),
    path('', include('centrales.urls')),
    path('', include('mediosaux.urls')),
    path('',include('delegaciones.urls')),
]
