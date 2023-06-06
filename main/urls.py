from django.urls import path
from . import views



urlpatterns = [
    path('', views.main, name='catalog'),
    path('product', views.product, name='product'),
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('login', views.main, name='login'),
]
