from django.urls import path
from .views import clients,services
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('backoffice/clientes',clients.list_clientes),
    path('backoffice/clientes/create', clients.create_client),
    path('backoffice/clientes/<int:client_id>',clients.client_details),
    path('backoffice/clientes/edit/<int:client_id>',clients.edit_client),
    path('backoffice/clientes/delete/<int:client_id>', clients.delete_client),
    path('backoffice/clientes/<int:client_id>/servicios/add',services.add_servicios_to_cliente),
    path('backoffice/clientes/<int:client_id>/servicios/remove',services.remove_servicios_to_cliente)
]