from django.urls import path
from . import views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('backoffice/servicios',views.list_servicios),
    path('backoffice/servicios/create', views.create_servicio),
    path('backoffice/servicios/<int:servicio_id>',views.servicio_details),
    path('backoffice/servicios/edit/<int:servicio_id>',views.edit_servicio),
    path('backoffice/servicios/delete/<int:servicio_id>', views.delete_servicio),
    path('backoffice/servicios/<int:servicio_id>/clientes/add',views.add_clientes_to_servicio),
    path('backoffice/servicios/<int:servicio_id>/clientes/remove',views.remove_clientes_to_servicio)
]