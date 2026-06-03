from django.urls import path
from . import views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('backoffice',views.show_backoffice)
]