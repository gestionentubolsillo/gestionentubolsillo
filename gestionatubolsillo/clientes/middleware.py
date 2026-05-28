#clientes/middleware.py
#Middleware personalizado para usuario_cliente

from .models import user_client
from django.http import HttpRequest

SESSION_KEY = '_user_client_id'

class ClientSessionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request:HttpRequest):
        client_id = request.session.get(SESSION_KEY)
        if client_id:
            try:
                request.user_client = user_client.objects.get(pk=client_id,is_active=True)
            except user_client.DoesNotExist:
                request.user_client = None
        else:
            request.user_client = None
        response = self.get_response(request)
        return response