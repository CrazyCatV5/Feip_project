from django.contrib.auth.models import User
from django.db.models import Exists, Count, Case, When
from django.shortcuts import render
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.fields import IntegerField
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import filters, generics, mixins, permissions
from main.models import Product, ProductColor, Brand, Size, Color, Category, ProductUser, Basket
from main.pagination import StandardResultsSetPagination
from main.serializers import ProductSerializer, BrandSerializer, SizeSerializer, ColorSerializer, \
    ProductColorSerializer, CategorySerializer, UserSerializer, RegisterSerializer, FavoriteSerializer, BasketSerializer
from rest_framework import viewsets


# Create your views here.


def main(request):
    return render(request, 'main/main.html')


def about(request):
    return render(request, 'main/about.html')


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
    filterset_fields = ["brand", "size", 'color', 'category', 'new', 'sale']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user.id
        if user == None:
            user = -1
        return Product.objects.annotate(is_favorite=Count(Case(When(productuser__user=user, then=1))))


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer


class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


class PictureViewSet(viewsets.ModelViewSet):
    queryset = ProductColor.objects.all()
    serializer_class = ProductColorSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = ProductUser.objects.all()
    serializer_class = FavoriteSerializer


class FavoriteProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ['name']
    filterset_fields = ["brand", "size", 'color', 'category', 'new', 'sale']
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
    def get(self, request):
        user = self.request.user.id
        if user == None:
            user = -1
        serializer = UserSerializer(User.objects.filter(id=user), many=True)
        return Response(serializer.data)
