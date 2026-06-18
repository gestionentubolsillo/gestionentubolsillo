from django.urls import path
from . import views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('backoffice/sugerencias',views.list_sugerencias),
    path('backoffice/sugerencias/self',views.list_own_sugerencias)

]