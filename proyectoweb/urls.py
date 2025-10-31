"""
URL configuration for proyectoweb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.urls import core_urlpatterns
from departamento import urls as departamento_urls
from direcciones import urls as direcciones_urls
from django.conf.urls.static import static
from django.conf import settings
from encuesta import urls as encuesta_urls
from incidencia import urls as incidencia_urls
from cuadrillas import urls as cuadrillas_urls
urlpatterns = [
    path('', include(core_urlpatterns)),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('registration.urls')),
    path('departamento/', include(departamento_urls.departamento_urlpatterns)),
    path('direcciones/', include(direcciones_urls.direcciones_urlpatterns)),
    path('encuesta/', include(encuesta_urls.encuesta_urlpatterns)),
    path('incidencia/', include(incidencia_urls.incidencia_urlpatterns)),
    path('cuadrillas/', include(cuadrillas_urls.cuadrillas_urlpatterns))
]    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
