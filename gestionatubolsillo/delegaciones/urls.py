from django.urls import path
from . import views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('backoffice/delegaciones',views.list_delegaciones),
    path('backoffice/delegaciones/create', views.create_delegacion),
    path('backoffice/delegaciones/<int:delegacion_id>',views.delegacion_details),
    path('backoffice/delegaciones/edit/<int:delegacion_id>',views.edit_delegacion),
    path('backoffice/delegaciones/delete/<int:delegacion_id>', views.delete_delegacion)
]