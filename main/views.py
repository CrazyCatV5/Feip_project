import json

from django.contrib.auth.models import User
from django.db.models import Exists, Count, Case, When
from django.shortcuts import render
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.fields import IntegerField
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import filters, generics, mixins, permissions
from main.models import Product, ProductColor, Brand, Size, Color, Category, ProductUser, Basket, Order, OrderPiece, \
    MainCategory, Contact
from main.pagination import StandardResultsSetPagination
from main.serializers import ProductSerializer, BrandSerializer, SizeSerializer, ColorSerializer, \
    ProductColorSerializer, CategorySerializer, UserSerializer, RegisterSerializer, FavoriteSerializer, \
    BasketSerializer, OrderSerializer, OrderPieceSerializer, MainCategorySerializer, ContactSerializer
from rest_framework import viewsets
from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from compressor.contrib.jinja2ext import CompressorExtension
import requests

def environment(**options):
    env = Environment(**options, extensions=[CompressorExtension])
    env.globals.update({
       'static': staticfiles_storage.url,
       'url_for': reverse,
    })
    return env

# Create your views here.


def main(request):
    context = requests.get('http://127.0.0.1:8000/api/v1/product/').json()
    return render(request, 'catalog.html', {'context': context})

def product(request):
    productInfo = requests.get('http://127.0.0.1:8000/api/v1/product/').json()
    WALink = "/"
    context = {
        'product': productInfo,
        'WALink': WALink,
    }
    return render(request, 'product.html', {'context': context})

def cart(request):
    context = requests.get('http://127.0.0.1:8000/api/v1/product/').json()
    return render(request, 'cart.html', {'context': context})

def checkout(request):
    context = requests.get('http://127.0.0.1:8000/api/v1/product/').json()
    return render(request, 'checkout.html', {'context': context})


class ProductAPI(APIView):
    def get(self, request):
        products = Product.objects.all()
        return Response({'products': ProductSerializer(products, many=True).data})

    def post(self, request):
        return Response()


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ['name']
    filterset_fields = ["brand", "size", 'color', 'category', 'new', 'sale','category__main_category']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user.id
        if user == None:
            user = -1
        return Product.objects.annotate(is_favorite=Count(Case(When(productuser__user=user, then=1))))

    @action(detail=False, methods=['get'], name='product_check')
    def product_check(self, request, *args, **kwargs):
        user = self.request.user.id
        if user == None:
            return Response(False)
        basket = Basket.objects.filter(user=user, product=request.GET['product'])
        if basket.first() == None:
            return Response(False)
        if basket[0].size.id == int(request.GET['size']) and basket[0].product.id == int(request.GET['product']) and basket[0].color.id == int(request.GET['color']):
            return Response(True)
        return Response(False)



class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = None


class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    pagination_class = None


class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    pagination_class = None


class PictureViewSet(viewsets.ModelViewSet):
    queryset = ProductColor.objects.all()
    serializer_class = ProductColorSerializer
    pagination_class = None


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    pagination_class = None


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = ProductUser.objects.all()
    serializer_class = FavoriteSerializer


class FavoriteProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ['name']
    filterset_fields = ["brand", "size", 'color', 'category', 'new', 'sale','category__main_category']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user.id
        if user == None:
            user = -1
        return Product.objects.filter(productuser__user=user).annotate(
            is_favorite=Count(Case(When(productuser__user=user, then=1))))


class BasketViewSet(viewsets.ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer


class MyBasketViewSet(viewsets.ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer

    def get_queryset(self):
        user = self.request.user.id
        if user == None:
            user = -1
        return Basket.objects.filter(user=user)


class UserCheckView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = None

    def get(self, request):
        user = self.request.user.id
        if user == None:
            user = -1
        serializer = UserSerializer(User.objects.filter(id=user), many=True)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['get'], name='create_order')
    def create_order(self, request, *args, **kwargs):
        user = self.request.user
        if user.id == None:
            queryset = Basket.objects.filter(user=user.id)
            serializer = OrderSerializer(queryset, many=True)
            return Response(serializer.data)
        user_basket = Basket.objects.filter(user=user)
        if user_basket.first() == None:
            queryset = Basket.objects.filter(user=user.id)
            serializer = BasketSerializer(queryset, many=True)
            return Response(serializer.data)
        if request.GET['address'] == '':
            new_order = Order.objects.create(user=user, email=user.email, comment=request.GET['comment'])
        else:
            new_order = Order.objects.create(user=user, email=user.email, comment=request.GET['comment'],
                                             address=request.GET['address'], way_to_get='доставка')
        sum = 0
        sale = 0
        count = 0
        for i in user_basket:
            OrderPiece.objects.create(order=new_order, product=i.product, size=i.size, color=i.color, count=i.count)
            sum += i.product.cost*i.count
            if i.product.sale == True:
                sale += (i.product.cost - i.product.sale_cost)*i.count
            count += i.count
        if new_order.order_piece.first() == None:
            new_order.delete()
            queryset = Basket.objects.filter(user=user.id)
            serializer = BasketSerializer(queryset, many=True)
            return Response(serializer.data)
        for i in user_basket:
            i.delete()
        new_order.count=count
        new_order.summ=sum
        new_order.sale=sale
        new_order.sale_summ=sum - sale
        new_order.save()

        serializer = OrderSerializer(Order.objects.filter(user=user), many=True)
        return Response(serializer.data)


class OrderPieceViewSet(viewsets.ModelViewSet):
    queryset = OrderPiece.objects.all()
    serializer_class = OrderPieceSerializer


class MainCategoryViewSet(viewsets.ModelViewSet):
    queryset = MainCategory.objects.all()
    serializer_class = MainCategorySerializer
    pagination_class = None


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    pagination_class = None
