from django.urls import path
from . import views
from .view_controller import trabajo_views, incidencia_views, acuda_views
urlpatterns = [
    #Rutas para diferentes tipos de partes
    #Trabajo
    path('backoffice/partes_trabajo',trabajo_views.list_partes_trabajo),
    path('backoffice/partes_trabajo/create',trabajo_views.create_parte_trabajo),
    path('backoffice/partes_trabajo/<int:p_trabajo_id>/actividades',trabajo_views.add_actividad_to_parte_trabajo, name='add_actividad_to_parte_trabajo'),
    path('backoffice/partes_trabajo/<int:parte_id>/close',trabajo_views.cerrar_parte_trabajo, name='cerrar_parte_trabajo'),
    path('backoffice/partes_trabajo/<int:parte_id>/relevar',trabajo_views.relevar_usuario_parte_trabajo,name='relevar_usuario_parte_trabajo'),
    path('backoffice/partes/<int:parte_id>',trabajo_views.view_parte_trabajo),

    #Incidencia
    path('backoffice/partes_incidencia',incidencia_views.list_partes_incidencia),
    path('backoffice/partes_incidencia/create',incidencia_views.create_parte_incidencia),
    path('backoffice/incidencias/<int:parte_id>',incidencia_views.view_parte_incidencia),

    #Acuda
    path('backoffice/informes_acuda',acuda_views.list_inf_acuda),
    path('backoffice/informes_acuda/create',acuda_views.create_inf_acuda),
    path('backoffice/acudas/<int:parte_id>',acuda_views.view_parte_acuda),


    #Inspeccion
    path('backoffice/partes_inspeccion',views.list_partes_inspeccion),
    
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