"""
URL configuration for website project.

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
from rest_framework import routers
from game import views

"""
This code specifies the URL path for the API. This was the final step that completes the building of the API.
"""
router = routers.DefaultRouter()
router.register(r'tiles', views.TileView, 'tile')
router.register(r'players', views.PlayerView, 'player')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('game.urls')),
    path('game/', include('game.urls')),
    path('api/', include(router.urls)),


]

handler404 = 'game.views.custom_404'
