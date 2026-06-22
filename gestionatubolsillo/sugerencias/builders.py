from typing import TypedDict
from users.models import User
from empresas.models import Empresa
from .models import Sugerencia
from datetime import datetime

class SugerenciaData(TypedDict):
    texto: str
    departamento: str
    usuario_creador:User
    usuario_referente:User



def build_sugerencia(data:SugerenciaData, fecha_creacion:datetime):
    texto = data.get('texto')
    departamento = data.get('departamento') or 'Sin Departamento'
    creador = data.get('usuario_creador')
    referente = data.get('usuario_referente')

    empresa:Empresa = referente.empresa

    sugerencia = Sugerencia()
    sugerencia.texto = texto
    sugerencia.departamento = departamento
    sugerencia.usuario_creador = creador
    sugerencia.usuario_referente = referente
    sugerencia.empresa = empresa
    sugerencia.fecha_creacion = fecha_creacion
    sugerencia.estado = 'pendiente'
    sugerencia.save()