from django.urls import path
from . import views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('backoffice/almacen',views.list_almacen),
    path('backoffice/almacen/create', views.create_almacen_item),
    path('backoffice/almacen/<int:item_id>',views.almacen_item_details),
    path('backoffice/almacen/edit/<int:item_id>',views.edit_almacen_item),
    path('backoffice/almacen/delete/<int:item_id>', views.delete_almacen_item)
]