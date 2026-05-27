from django.urls import path
from . import views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('backoffice/empresas',views.list_empresas),
    path('backoffice/empresas/create', views.create_empresa),
    path('backoffice/empresas/<int:empresa_id>',views.details_empresa),
    path('backoffice/empresas/edit/<int:empresa_id>',views.edit_empresa),
    path('backoffice/empresas/delete/<int:empresa_id>', views.delete_empresa)
]