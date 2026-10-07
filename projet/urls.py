"""
URL configuration for projet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path,include
from application import views
from django.conf import settings
from django.conf.urls.static import static
from authentification.views import * # On importe la vue directement
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='connexion', permanent=False)),
    path ('home/',views.acceuil , name = 'acceuil' ),
    path ('remove/', views.emove , name = 'emove'),
    path ('code/', views.code , name = 'code'),
    path( 'son/', views.son , name = 'son'),
    path("transcription/", views.transcription, name="transcription"),
    path("convertisseur/", views.convertisseur, name="convertisseur"),
     # On inclut proprement les URLs de notre nouvelle application
    path('auth/', include('authentification.urls')), 

]
if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    # Permet à Django de servir les images
