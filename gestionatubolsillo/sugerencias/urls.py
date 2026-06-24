from django.urls import path
from . import views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('backoffice/sugerencias',views.list_sugerencias),
    path('backoffice/sugerencias/self',views.list_own_sugerencias),
    path('backoffice/sugerencias/create', views.create_sugerencia),
    path('backoffice/sugerencias/<int:sugerencia_id>/delete',views.delete_sugerencia),
    path('backoffice/sugerencias/<int:sugerencia_id>',views.details_sugerencia)

]