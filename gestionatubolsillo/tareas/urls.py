from django.urls import path
from . import views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('backoffice/tareas',views.list_tareas),
    path('backoffice/tareas/create',views.create_tarea),
    path('backoffice/tareas/<int:tarea_id>',views.details_tarea),
    path('backoffice/tareas/<int:tarea_id>/delete', views.delete_tarea),
    path('backoffice/tareas/<int:tarea_id>/changestatus', views.change_state_tarea),
    path('backoffice/tareas/listados',views.lista_listados_de_usuarios),
    path('backoffice/tareas/listados/create',views.create_list_usuarios),
    path('backoffice/tareas/listados/<int:lista_id>/edit',views.edit_list_usuarios)
]