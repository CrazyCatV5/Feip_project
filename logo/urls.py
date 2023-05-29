"""logo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from main.views import *
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'product', ProductViewSet)
router.register(r'brand', BrandViewSet)
router.register(r'size', SizeViewSet)
router.register(r'color', ColorViewSet)
router.register(r'image', PictureViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'user', UserViewSet)
router.register(r'favorite', FavoriteViewSet)
router.register(r'user_favorite', FavoriteProductViewSet)
router.register(r'basket', BasketViewSet)
router.register(r'my_basket', MyBasketViewSet)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('api/v1/', include(router.urls)),
    path('api/v1/drf-auth/', include('rest_framework.urls')),
    path('api/v1/register/', RegisterView.as_view()),
    path('api/v1/user_check', UserCheckView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
