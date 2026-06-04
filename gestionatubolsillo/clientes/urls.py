from django.urls import path
from . import views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('backoffice/clientes',views.list_clientes),
    path('backoffice/clientes/create', views.create_client),
    path('backoffice/clientes/<int:client_id>',views.client_details),
    path('backoffice/clientes/edit/<int:client_id>',views.edit_client),
    path('backoffice/clientes/delete/<int:client_id>', views.delete_client)
]