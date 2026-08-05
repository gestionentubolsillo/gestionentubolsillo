import jwt
from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpRequest
from users.models import User 


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request:HttpRequest):
        token = request.COOKIES.get('jwt_token')
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                token_version = payload.get('token_version')

                # Fetch the user from the database
                user = User.objects.filter(pk=user_id).first()

                if user and user.token_version == token_version:
                    request.user = user
                else:
                    logout(request)  # Invalidate the session if token version doesn't match
            except jwt.ExpiredSignatureError:
                logout(request)  # Token has expired, log out the user
            except jwt.InvalidTokenError:
                logout(request)  # Invalid token, log out the user

        response = self.get_response(request)
        return response