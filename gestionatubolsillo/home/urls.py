from django.urls import path
from . import views

urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('', views.home, name='home'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]