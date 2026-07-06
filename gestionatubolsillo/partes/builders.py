from datetime import datetime
from typing import NotRequired, TypedDict
from clientes.models import Cliente
from empresas.models import Empresa
from servicios.models import Servicio
from users.models import User
from centrales.models import Central
from .models import Parte_Trabajo, Linea_Parte_Trabajo, Parte_Incidencia, Parte_Inspeccion, Informe_Acuda,Parte


class GeneralParteData(TypedDict):
    usuario_asignado: User
    cliente: Cliente
    empresa: Empresa

class ParteTrabajoData(TypedDict):
    general:GeneralParteData
    servicio:Servicio
    observaciones:str


def _build_general_parte(parte:Parte, data: GeneralParteData, user:User, created_at:datetime)->None:
    parte.usuario_creador = user
    parte.cuenta = user.cuenta
    parte.fecha_creacion = created_at
    parte.usuario_asignado = data.get('usuario_asignado')
    parte.cliente = data.get('cliente')
    parte.empresa = data.get('empresa')



def build_parte_trabajo(data: ParteTrabajoData,user:User,created_at:datetime,fecha_inicio_registrada:datetime | None = None) -> Parte_Trabajo:
    parte = Parte_Trabajo()
    _build_general_parte(parte, data.get('general'), user, created_at)
    parte.fecha_inicio_registrada = fecha_inicio_registrada if fecha_inicio_registrada is not None else created_at
    parte.servicio = data.get('servicio')
    parte.observaciones = data.get('observaciones')
    parte.save()
    
    return parte

class LineaParteData(TypedDict):
    actividad : str
    extra_info : str
    fecha_registrada : NotRequired[datetime]
    parte_trabajo : Parte_Trabajo

def build_linea_parte_trabajo(data:LineaParteData,created_at:datetime)->Linea_Parte_Trabajo:
    linea = Linea_Parte_Trabajo()
    linea.actividad = data.get('actividad')
    linea.extra_info = data.get('extra_info')
    linea.fecha_registrada = data.get('fecha_registrada') if data.get('fecha_registrada') is not None else created_at
    linea.fecha_creacion = created_at
    linea.parte_trabajo = data.get('parte_trabajo')
    linea.save()

    return linea



class IncidenciaData(TypedDict):
    general : GeneralParteData
    texto_incidencia : str
    fecha_hora_incidencia : NotRequired[datetime]

def build_parte_incidencia(data:IncidenciaData,user:User,created_at:datetime)->Parte_Incidencia:
    parte = Parte_Incidencia()
    _build_general_parte(parte, data.get('general'), user, created_at)
    parte.fecha_hora_incidencia = data.get('fecha_hora_incidencia') if data.get('fecha_hora_incidencia') is not None else created_at
    parte.texto_incidencia = data.get('texto_incidencia')
    parte.save()

    return parte



class AcudaData(TypedDict):
    general: GeneralParteData
    descripcion:str
    central: Central

def build_parte_acuda(data:AcudaData,user:User,created_at:datetime)->Informe_Acuda:
    parte = Informe_Acuda()
    _build_general_parte(parte, data.get('general'), user, created_at)
    parte.central = data.get('central')
    parte.descripcion = data.get('descripcion')
    parte.save()

    return parte
