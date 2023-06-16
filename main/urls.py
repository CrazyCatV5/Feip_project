from django.urls import path
from . import views



urlpatterns = [
    path('<int:page>', views.main, name='catalog'),
    path('product/<int:id>', views.product, name='product'),
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
]
