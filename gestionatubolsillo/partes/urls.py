from django.urls import path
from .views import trabajo_views, incidencia_views, acuda_views,inspeccion_views
from .views.general_views import general,trabajo_general,acuda_general,incidencia_general
urlpatterns = [
    #Rutas para diferentes tipos de partes
    #Trabajo
    path('backoffice/partes_trabajo',trabajo_views.list_partes_trabajo),
    path('backoffice/partes_trabajo/<int:parte_id>',trabajo_views.parte_trabajo_details),
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
    path('backoffice/informes_acuda/<int:parte_id>',acuda_views.parte_acuda_details),
    path('backoffice/acudas/<int:parte_id>',acuda_views.view_parte_acuda),


    #Inspeccion
    path('backoffice/partes_inspeccion',inspeccion_views.list_partes_inspeccion),
    
    #General
    path('backoffice/informes',general.dashboard_informes),
    path('backoffice/informes/incidencias',incidencia_general.list_informes_informe_incidencia),

    #General Trabajo
    path('backoffice/informes/trabajo',trabajo_general.list_informes_informe_trabajo),
    path('backoffice/informes/trabajo/horas_cliente',trabajo_general.list_informes_informe_trabajo_horas_cliente),
    path('backoffice/informes/trabajo/horas_tecnico',trabajo_general.list_informes_informe_trabajo_horas_tecnico),
    path('backoffice/informes/trabajo/resumen_tecnico',trabajo_general.list_informes_informe_trabajo_resumen),

    #General Acudas
    path('backoffice/informes/acudas',acuda_general.list_informes_informe_acuda),
    path('backoffice/informes/acudas/cliente',acuda_general.list_informes_informe_acuda_cliente),
    path('backoffice/informes/acudas/tecnico',acuda_general.list_informes_informe_acuda_tecnico),
    

    #Rutas de ayuda de js forms
    path('ajax/get_servicios_por_cliente/<int:cliente_id>',general.get_servicios_por_cliente),
]