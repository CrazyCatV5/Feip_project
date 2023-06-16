from django.contrib.auth.models import User
from django.db import models
from colorfield.fields import ColorField
from django.utils import timezone


# Create your models here.
class MainCategory(models.Model):
    main_category = models.TextField('основная_категория', max_length=20)

    def __str__(self):
        return str(self.main_category)


class Category(models.Model):
    category = models.TextField('категория', max_length=20)
    main_category= models.ForeignKey(MainCategory,related_name="category", on_delete=models.DO_NOTHING, null=True, default=1)

    def __str__(self):
        return str(self.category)


class Size(models.Model):
    size = models.CharField('Размер', max_length=8)

    def __str__(self):
        return str(self.size)


class Color(models.Model):
    name = models.TextField('Цвет', max_length=20)
    color = models.BigIntegerField('код (десятичный)',
                                   default=4278190080, )  # цвет храним как десятеричную версию хеша ARGB

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.TextField('Бренд', max_length=20)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.TextField('Название', max_length=20)
    article = models.TextField('Артикул', max_length=20)
    cost = models.FloatField('Цена', )
    sale_cost = models.FloatField('Скидочная_цена', )
    cost_formatted = models.TextField('Цена (строка)', max_length=20)
    sale_cost_formatted = models.TextField('Cкидочная_цена (строка)', max_length=20)
    new = models.BooleanField('Новый?', )
    sale = models.BooleanField('Скидка?', )
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    description = models.TextField('Описание')
    size = models.ManyToManyField(Size)
    color = models.ManyToManyField(Color, through='ProductColor')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    favorite = models.ManyToManyField(User, through='ProductUser', related_name='product_favorite')
    basket_piece = models.ManyToManyField(User, through='Basket', related_name='product_basket')

    def __str__(self):
        return self.name


class ProductColor(models.Model):
    image = models.ImageField('Изображение', upload_to='products')
    name = models.TextField('Название', max_length=20)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = [["product", "color"]]


class ProductUser(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.product) + ' ' + str(self.user)

    class Meta:
        unique_together = [["product", "user"]]


class Basket(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.product) + ' ' + str(self.user) + ' ' + str(self.color) + ' ' + str(self.size)

    class Meta:
        unique_together = [["product", "user", "color", "size"]]


class Order(models.Model):
    status_choices = (
        ('оформлен', 'оформлен'),
        ('готов', 'готов'),
        ('доставлен', 'доставлен')
    )
    way_choices = (
        ('самовывоз', 'самовывоз'),
        ('доставка', 'доставка')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField('почта', max_length=200)
    address = models.TextField("Адрес", max_length=200, default='')
    count = models.IntegerField("Количество товара", default=0)
    summ = models.FloatField("Цена", default=0)
    sale = models.FloatField("Скидка", default=0)
    sale_summ = models.FloatField("Цена со скидкой", default=0)
    comment = models.TextField("Коментарий", default='')
    order_piece = models.ManyToManyField(Product, through='OrderPiece')
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField("Статус", max_length=300, choices=status_choices, default="оформлен")
    way_to_get = models.CharField(max_length=300, choices=way_choices, default="самовывоз")

    def __str__(self):
        return str(self.user) + ' ' + str(self.pk)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(way_to_get="доставка") & ~models.Q(address='') | (models.Q(way_to_get="самовывоз") & models.Q(address='')), name='way_to_get_address')]


class OrderPiece(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.order) + ' ' + str(self.product)+ ' ' + str(self.color)+ ' размер:' + str(self.size)

    class Meta:
        unique_together = [["product", "order", "color", "size"]]


class Contact(models.Model):
    name = models.TextField(max_length=30)
    data = models.TextField(max_length=30)
    image = models.ImageField('Изображение', upload_to='contacts_and_media', null=True)

    def __str__(self):
        return str(self.name)
