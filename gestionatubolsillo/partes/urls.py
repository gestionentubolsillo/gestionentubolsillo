from django.urls import path
from . import views
urlpatterns = [
    #Rutas para diferentes tipos de partes
    path('backoffice/partes_trabajo',views.list_partes_trabajo),
    path('backoffice/partes_incidencia',views.list_partes_incidencia),
    path('backoffice/informes_acuda',views.list_inf_acuda),
    path('backoffice/partes_inspeccion',views.list_partes_inspeccion),
    path('backoffice/partes',views.view_parte_trabajo),
    path('backoffice/incidencias',views.view_parte_incidencia),
    path('backoffice/acudas',views.view_parte_acuda),

    path('backoffice/partes_trabajo/create',views.create_parte_trabajo),

    #Rutas desde informes
    
    path('backoffice/informes',views.dashboard_informes),
    path('backoffice/informes/trabajo',views.list_informes_informe_trabajo),
    #path('backoffice/informes/incidencias',views.list_informes_informe_incidencia),
    #path('backoffice/informes/acudas',views.list_informes_informe_acuda),
    path('backoffice/informes/trabajo/horas_cliente',views.list_informes_informe_trabajo_horas_cliente),
    path('backoffice/informes/trabajo/horas_tecnico',views.list_informes_informe_trabajo_horas_tecnico),
    path('backoffice/informes/trabajo/resumen_tecnico',views.list_informes_informe_trabajo_resumen),
    #path('backoffice/informes/acudas/cliente',views.list_informes_informe_acuda_cliente),
    #path('backoffice/informes/acudas/tecnico',views.list_informes_informe_acuda_tecnico),
    #path('backoffice/informes/nfc',views.list_informes_informe_nfc),
    #path('backoffice/informes/almacen',views.list_informes_informe_almacen),

    #Rutas de ayuda de js forms
    path('ajax/get_servicios_por_cliente/<int:cliente_id>',views.get_servicios_por_cliente),
]