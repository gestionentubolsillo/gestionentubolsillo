from django.urls import path
from . import views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('backoffice/medios_auxiliares',views.list_medios_auxiliares),
    path('backoffice/medios_auxiliares/create', views.create_medio_auxiliar),
    path('backoffice/medios_auxiliares/<int:medio_auxiliar_id>',views.medio_auxiliar_details),
    path('backoffice/medios_auxiliares/edit/<int:medio_auxiliar_id>',views.edit_medio_auxiliar),
    path('backoffice/medios_auxiliares/delete/<int:medio_auxiliar_id>', views.delete_medio_auxiliar)
]