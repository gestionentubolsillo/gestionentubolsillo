from django.urls import path
from .views import user_views, cuadrante_views, perm_views, service_views, tarea_views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    #User
    path('backoffice/users',user_views.lista_users),
    path('backoffice/users/create', user_views.create_user),
    path('backoffice/users/<int:user_id>',user_views.user_details),
    path('backoffice/users/edit/<int:user_id>',user_views.edit_user),
    path('backoffice/users/delete/<int:user_id>',user_views.delete_user),
    #Permisos
    path('backoffice/users/permissions/edit/<int:user_id>',perm_views.alter_user_permissions),
    path('backoffice/users/permissions/<int:user_id>',perm_views.view_user_permissions),
    #Servicios
    path('backoffice/users/<int:user_id>/services',service_views.list_services_of_user),
    path('backoffice/users/<int:user_id>/services/assign',service_views.assign_services_to_user),
    path('backoffice/users/<int:user_id>/services/remove',service_views.remove_services_to_user),
    #Cuadrantes
    path('backoffice/users/<int:user_id>/cuadrantes',cuadrante_views.list_cuadrantes_of_user),
    path('backoffice/users/<int:user_id>/cuadrantes/create',cuadrante_views.create_cuadrante),
    path('backoffice/users/<int:user_id>/cuadrantes/<int:cuadrante_id>',cuadrante_views.cuadrante_details),
    path('backoffice/users/<int:user_id>/cuadrantes/<int:cuadrante_id>/pdf',cuadrante_views.show_cuadrante_pdf,name='show_pdf'),
    path('backoffice/users/<int:user_id>/cuadrantes/<int:cuadrante_id>/delete',cuadrante_views.delete_cuadrante),
    #Tareas
    path('backoffice/users/<int:user_id>/tareas',tarea_views.list_tareas_user)
]