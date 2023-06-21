from django.urls import path
from django.shortcuts import redirect
from . import views



urlpatterns = [
    # path('api/v1/drf-auth/login/', lambda req: redirect('login/')),
    path('', lambda req: redirect('catalog', page=1)),
    path('<int:page>', views.catalog, name='catalog'),
    path('category/<str:categoryName>/', views.category, name='category'),
    path('category/<str:categoryName>/<int:page>', views.category, name='category'),
    path('search/', views.search, name='search'),
    path('search/<int:page>/', views.search, name='search'),
    path('product/<int:id>', views.product, name='product'),
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('login', views.login, name='login'),
    # path('login/', views.LoginView.as_view(template_name="login.html", authentication_form=UserLoginForm), name='login')
]
