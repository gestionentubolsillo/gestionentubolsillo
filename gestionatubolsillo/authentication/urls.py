from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
urlpatterns = [
    # Aquí puedes agregar las rutas de tu aplicación
    path('login', views.login, name='login'),
    path('logout',views.logout_view,name='logout')
]