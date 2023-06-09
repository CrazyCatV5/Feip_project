import json
import math

from django.contrib.auth.models import User
from django.db.models import Exists, Count, Case, When
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
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

def getFormattedCost(cost):
    cost_formatted = str(int(cost) % 1000) + " ₽"
    k = 5
    while(cost > 10**3):
        cost_formatted = str(int(cost) // 1000 % 1000) + " " + cost_formatted.zfill(k)
        cost = cost // 1000
        k += 4
    return cost_formatted

def getPaginationInfo(productInfo, page):
    lastPage = math.ceil(productInfo.get('count') / 12)
    leftPages = min(page - 1, 3)
    rightPages = min(lastPage - page, 3)
    leftArrow = False
    rightArrow = False
    if (page - 1 > 3):
        leftArrow = True
    if (lastPage - page > 3):
        rightArrow = True
    return [lastPage, leftPages, rightPages, leftArrow, rightArrow]

def getCategoryID(name):
    categoryList = requests.get('http://127.0.0.1:8000/api/v1/category').json()
    for item in categoryList:
        if (item.get('category') == name):
            return item.get('id')
    return -1

# Create your views here.

def login(request, errors=""):
    return render(request, 'login.html')

def catalog(request, page):
    productInfo = requests.get('http://127.0.0.1:8000/api/v1/product/?page=' + str(page)).json()
    if ('count' not in productInfo):
        return HttpResponseNotFound("Страницы не существует")
    [lastPage, leftPages, rightPages, leftArrow, rightArrow] = getPaginationInfo(productInfo, page)
    context = {
        'products': productInfo,
        'currentPage': page,
        'leftPages': leftPages,
        'rightPages': rightPages,
        'leftArrow': leftArrow,
        'rightArrow': rightArrow,
        'lastPage': lastPage,
        'parentRoute': '/',
    }
    return render(request, 'catalog.html', {'context': context})

def category(request, categoryName, page=1):
    categoryID = getCategoryID(categoryName)
    productInfo = requests.get(
        'http://127.0.0.1:8000/api/v1/product/?page=' + str(page)
        + '&category=' + str(categoryID)
        ).json()
    if ('count' not in productInfo):
        return HttpResponseNotFound("Страницы не существует")
    [lastPage, leftPages, rightPages, leftArrow, rightArrow] = getPaginationInfo(productInfo, page)
    context = {
        'products': productInfo,
        'currentPage': page,
        'leftPages': leftPages,
        'rightPages': rightPages,
        'leftArrow': leftArrow,
        'rightArrow': rightArrow,
        'lastPage': lastPage,
        'parentRoute': '/category/' + categoryName + '/',
        'categoryName': categoryName,
    }
    return render(request, 'category.html', {'context': context})

def search(request, page = 1, query = ''):
    if (request.GET.get('search')):
        query = request.GET.get('search')
    if (request.GET.get('page')):
        page = int(request.GET.get('page'))
    queryString = '?search=' + query + '&page=' + str(page)
    productInfo = requests.get(
        'http://127.0.0.1:8000/api/v1/product/' + queryString
        ).json()
    if ('count' not in productInfo):
        return HttpResponseNotFound("Страницы не существует")
    [lastPage, leftPages, rightPages, leftArrow, rightArrow] = getPaginationInfo(productInfo, page)
    context = {
        'products': productInfo,
        'currentPage': page,
        'leftPages': leftPages,
        'rightPages': rightPages,
        'leftArrow': leftArrow,
        'rightArrow': rightArrow,
        'lastPage': lastPage,
        'parentRoute': '/search/?search=' + query + '&page=',
        'categoryName': 'Результаты по запросу: \"' + query + '\"',
    }
    return render(request, 'search.html', {'context': context})

def product(request, id):
    user = None
    if request.user.is_authenticated:
        user = request.user.id
    product = requests.get('http://127.0.0.1:8000/api/v1/product/' + str(id) + '/').json()
    basket = requests.get('http://127.0.0.1:8000/api/v1/basket/').json()
    my_basket = []
    products = []
    count = 0
    cost = 0
    for item in basket:
        if (item.get("user") == user and item.get("product") == product.get("id")):
            my_basket.append(item)
    if (not product.get('id')):
        return HttpResponseNotFound("Страницы не существует")
    WALink = "/"
    context = {
        'basket': my_basket,
        'product': product,
        'WALink': WALink,
    }
    return render(request, 'product.html', {'context': context})

def checkout(request):
    user = None
    if request.user.is_authenticated:
        user = request.user.id
    basket = requests.get('http://127.0.0.1:8000/api/v1/basket/').json()
    sizes = requests.get('http://127.0.0.1:8000/api/v1/size/').json()
    colors = requests.get('http://127.0.0.1:8000/api/v1/color/').json()
    my_basket = []
    products = []
    count = 0
    cost = 0
    for item in basket:
        if (item.get("user") == user):
            my_basket.append(item)
            product = requests.get('http://127.0.0.1:8000/api/v1/product/' + str(item.get('product')) + '/').json()
            products.append(product)
            count += 1
            cost += product.get("cost")

    cost_formatted = getFormattedCost(cost)
    context = {
        'basket': my_basket,
        'products': products,
        'sizes': sizes,
        'colors': colors,
        'total': {
            'count': count,
            'cost': cost_formatted,
        }
    }
    return render(request, 'checkout.html', {'context': context})

def cart(request):
    user = None
    if request.user.is_authenticated:
        user = request.user.id
    basket = requests.get('http://127.0.0.1:8000/api/v1/basket/').json()
    sizes = requests.get('http://127.0.0.1:8000/api/v1/size/').json()
    colors = requests.get('http://127.0.0.1:8000/api/v1/color/').json()
    my_basket = []
    products = []
    count = 0
    cost = 0
    for item in basket:
        if (item.get("user") == user):
            my_basket.append(item)
            product = requests.get('http://127.0.0.1:8000/api/v1/product/' + str(item.get('product')) + '/').json()
            products.append(product)
            count += 1
            cost += product.get("cost")

    cost_formatted = getFormattedCost(cost)
    context = {
        'basket': my_basket,
        'products': products,
        'sizes': sizes,
        'colors': colors,
        'total': {
            'count': count,
            'cost': cost_formatted,
        }
    }
    return render(request, 'cart.html', {'context': context})


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
        print(int(request.GET['size']))
        print(basket[0].size.id)
        print(int(request.GET['product']))
        print(basket[0].product.id)
        print(int(request.GET['color']))
        print(basket[0].color.id)
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

    # def create(self, request, *args, **kwargs):
    #     response = super(BasketViewSet, self).create(request, *args, **kwargs)
    #     # here may be placed additional operations for
    #     # extracting id of the object and using reverse()
    #     return HttpResponseRedirect(self.request.path_info)


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
