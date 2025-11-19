from django.urls import path
from .views import SignUpView, ProfileUpdate, EmailUpdate
from django.contrib import admin
from registration import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
''' Acá deben agregar las rutas para las funciones que creen en views.py '''
urlpatterns = [
    path('signup/', SignUpView.as_view(), name="signup"),
    path('profile/', ProfileUpdate.as_view(), name="profile"),
    path('profile/email/', EmailUpdate.as_view(), name="profile_email"),
    path('profile_edit/', views.profile_edit, name='profile_edit'),
    path('main_usuario/', views.main_usuario, name='main_usuario'),
    path('crear_usuario/', views.crear_usuario, name='crear_usuario'),
    path('ver_usuario/<user_id>/', views.ver_usuario, name='ver_usuario'),
    path('editar_usuario/<user_id>/', views.editar_usuario, name='editar_usuario'),
    path('bloquear_desbloquear_usuario/<int:user_id>/', views.bloquear_desbloquear_usuario, name ='bloquear_desbloquear_usuario'),
    path('usuarios_bloqueados/', views.main_usuario_bloqueados, name = 'main_usuario_bloqueados'),
    path('profile_elimina/<int:profile_id>/', views.profile_elimina, name='profile_elimina'),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    ]