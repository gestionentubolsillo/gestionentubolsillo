from django.urls import path
from . import views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('backoffice/admin', views.list_logs, name='list_logs'),
]