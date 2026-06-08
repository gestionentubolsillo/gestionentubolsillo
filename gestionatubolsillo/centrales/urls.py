from django.urls import path
from . import views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('backoffice/centrales',views.list_centrales),
    path('backoffice/centrales/create', views.create_central),
    path('backoffice/centrales/<int:central_id>',views.central_details),
    path('backoffice/centrales/edit/<int:central_id>',views.edit_central),
    path('backoffice/centrales/delete/<int:central_id>', views.delete_central)
]