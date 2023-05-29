import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logo.settings')

import django

django.setup()

import random
from django.utils.crypto import get_random_string
from logo.settings import DATABASE_PATH
from main.models import Product, ProductColor, Color, Size, Brand, Category
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("DROP SCHEMA public CASCADE;")
    cursor.execute("CREATE SCHEMA public;")

def main():
    os.system('python manage.py makemigrations')
    os.system('python manage.py migrate')
    ProductColor.objects.all().delete()
    Product.objects.all().delete()
    Color.objects.all().delete()
    Category.objects.all().delete()
    Size.objects.all().delete()
    Brand.objects.all().delete()
    for i in range(10):
        size = Size(size=i * 5 + 45)
        size.save()
    for i in range(4):
        name = ['штаны', "куртки", "ботинки", "шляпы"]
        category = Category(category=name[i])
        category.save()
    for i in range(5):
        name = ['красный', "черный", "синий", "желтый", "зеленый"]
        color = Color(name=name[i], color=4278190080 // (i + 1))
        color.save()
    color = Color.objects.all()
    for i in range(10):
        brand = Brand(name=get_random_string(10))
        brand.save()
    for i in range(100):
        booll = [True, False]
        cost = random.randrange(1000, 100000)
        brand = Brand.objects.all()
        category = Category.objects.all()
        size = Size.objects.all()
        product = Product.objects.create(cost=cost, sale_cost=cost - cost // 25,
                                         new=random.choice(booll), sale=random.choice(booll),
                                         brand=brand[random.randrange(1, 9)],
                                         description=get_random_string(50))
        if i < 25:
            product.name = 'штаны' + str(i)
            product.article = ('штаны' + str(i))
            product.category = (category[0])
        elif i < 50:
            product.name = 'куртка' + str(i)
            product.article = ('куртка' + str(i))
            product.category = (category[1])
        elif i < 75:
            product.name = 'ботинки' + str(i)
            product.article = ('ботинки' + str(i))
            product.category = (category[2])
        else:
            product.name = 'шляпа' + str(i)
            product.article = ('шляпа' + str(i))
            product.category = (category[3])
        product.color.add(color[random.randrange(0, 2)], through_defaults={'name': "изображение" + str(i),
                                                               'image': 'products/seed/' + str(
                                                                               i + 1) + '.png'})
        product.size.add(size[random.randrange(1, 9)])
        product.save()

    product = Product.objects.all()
    for i in range(99):
        pc = ProductColor(image='products/seed/' + str(i + 3) + '.png', name="изображение" + str(i)+ str(i),
                          product=product[i+1], color=color[random.randrange(2, 4)])
        pc.save()


if __name__ == '__main__':
    main()
