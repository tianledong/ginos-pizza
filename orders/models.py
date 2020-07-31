from django.db import models
from django.contrib.auth.models import User

SIZE_SETTING = (('S', 'Small'), ('O', 'One Size '), ('L', 'Large'))
STATE_SETTING = (('AL', 'Alabama'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'),
                 ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District of Columbia'), ('FL', 'Florida'),
                 ('GA', 'Georgia'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'),
                 ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
                 ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
                 ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'),
                 ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'),
                 ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'),
                 ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'),
                 ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'),
                 ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming'))


class Topping(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Category(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return self.category


class Product(models.Model):
    name = models.CharField(max_length=64)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, max_length=64)
    price = models.DecimalField(decimal_places=2, max_digits=1000, null=True, blank=True)
    priceLarge = models.DecimalField(decimal_places=2, max_digits=1000, null=True, blank=True)
    one_size = models.BooleanField(default=False)
    topping_num = models.IntegerField(default=0)
    is_allowed_additional = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f'{self.name} - {self.category}'

    def img_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Additional(models.Model):
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} + ${self.price}"


class OrderProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, max_length=64)
    quantity = models.IntegerField(default=1)
    toppings = models.ManyToManyField(Topping, blank=True)
    additional = models.ManyToManyField(Additional, blank=True)
    size = models.CharField(choices=SIZE_SETTING, max_length=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.product} x {self.quantity} for {self.user.username}'

    def get_price(self):
        if self.additional:
            additional_price = sum([a.price for a in self.additional.all()])
            if self.size == 'L':
                return (self.product.priceLarge + additional_price) * self.quantity
            return (self.product.price + additional_price) * self.quantity
        else:
            if self.size == 'L':
                return self.product.priceLarge * self.quantity
            return self.product.price * self.quantity


class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name_on_card = models.CharField(max_length=64)
    address = models.CharField(max_length=100)
    address1 = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=2, choices=STATE_SETTING)
    zip = models.IntegerField()


class Payment(models.Model):
    stripe_id = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    billing_address = models.ForeignKey(BillingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    orderProduct = models.ManyToManyField(OrderProduct)
    finished = models.BooleanField(default=False)
    orderTime = models.DateTimeField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def total_price(self):
        total = 0
        for item in self.orderProduct.all():
            total += item.get_price()
        return total

    def total_item(self):
        total = 0
        for product in self.orderProduct.all():
            total += product.quantity
        return total
