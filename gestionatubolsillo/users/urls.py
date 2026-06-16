from django.urls import path
from . import views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('backoffice/users',views.lista_users),
    path('backoffice/users/create', views.create_user),
    path('backoffice/users/<int:user_id>',views.user_details),
    path('backoffice/users/edit/<int:user_id>',views.edit_user),
    path('backoffice/users/delete/<int:user_id>',views.delete_user),
    path('backoffice/users/permissions/edit/<int:user_id>',views.alter_user_permissions),
    path('backoffice/users/permissions/<int:user_id>',views.view_user_permissions),
    path('backoffice/users/<int:user_id>/services',views.list_services_of_user),
    path('backoffice/users/<int:user_id>/services/assign',views.assign_services_to_user),
    path('backoffice/users/<int:user_id>/services/remove',views.remove_services_to_user)
]