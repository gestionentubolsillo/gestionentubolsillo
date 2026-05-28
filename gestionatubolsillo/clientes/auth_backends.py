#clientes/auth_backends.py
#Backend personalizado para usuario_cliente

from .models import user_client
from django.http import HttpRequest

class ClientBackend:

    def authenticate(self,request:HttpRequest,
                     username=None,password=None, **kwargs):
        try:
            user = user_client.objects.get(username=username)
            if user.check_password(password) and user.is_active:
                return user
        except user_client.DoesNotExist:
            return None
        
    def get_user(self, user_id):
        try:
            return user_client.objects.get(pk=user_id)
        except user_client.DoesNotExist:
            return None