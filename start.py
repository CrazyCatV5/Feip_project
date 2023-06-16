import os
import django
os.environ["DJANGO_SETTINGS_MODULE"] = "logo.settings"
django.setup()
from django.contrib.auth.models import User
import random
from django.utils.crypto import get_random_string
from main.models import Product, ProductColor, Color, Size, Brand, Category, MainCategory, Contact
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
    MainCategory.objects.all().delete()
    for i in range(3):
        name = ['остальное', 'одежда', "аксессуары"]
        main_category = MainCategory(main_category=name[i])
        main_category.save()
    sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']
    for i in range(7):
        size = Size(size=sizes[i])
        size.save()
    for i in range(4):
        name = ['штаны', "куртки", "ботинки", "шляпы"]
        main_category = MainCategory.objects.all()

        if i == 0 or i == 1:
            category = Category(category=name[i], main_category=main_category[1])
        elif i == 3:
            category = Category(category=name[i], main_category=main_category[2])
        else:
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
        cost_formatted = str(int(cost) // 1000) + " " + str(int(cost) % 1000).zfill(3) + " ₽"
        sale_cost = cost - cost // 25
        sale_cost_formatted = str(int(sale_cost) // 1000) + " " + str(int(sale_cost) % 1000).zfill(3) + " ₽"
        brand = Brand.objects.all()
        category = Category.objects.all()
        size = Size.objects.all()
        product = Product.objects.create(cost=cost, cost_formatted=cost_formatted, 
                                         sale_cost=sale_cost, sale_cost_formatted=sale_cost_formatted,
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
        product.size.add(size[random.randrange(1, 7)])
        product.save()

    product = Product.objects.all()
    for i in range(99):
        pc = ProductColor(image='products/seed/' + str(i + 3) + '.png', name="изображение" + str(i) + str(i),
                          product=product[i + 1], color=color[random.randrange(2, 4)])
        pc.save()

    for i in range(7):
        name = ['телефон', 'email', "telegram", "instagram", "vk", "youtube", "whatsapp"]
        data = ['+7(900)900-90-90', "admin@admin.admin"]
        if i < 2:
            contact = Contact(name=name[i], data=data[i])
        else:
            contact = Contact(name=name[i], data=name[i], image='contacts_and_media/mono/' + name[i] + '.png')
        contact.save()
    user = User.objects.create(username='root', email='root@root.root', first_name='root', last_name='root')
    user.set_password('root')
    user.save()
    user = User.objects.create(username='admin', email='admin@admin.admin', first_name='admin', last_name='admin', is_superuser=True, is_staff=True)
    user.set_password('admin')
    user.save()


if __name__ == '__main__':
    main()
