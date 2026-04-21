from decimal import Decimal
from django.db import models
from products.models import Product
from users.models import User
from phonenumber_field.modelfields import PhoneNumberField
from orders.contants import delivery_choises, payment_choises, company_locker_choises

class Order(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.SET_DEFAULT,unique=False, blank=True, null=True, verbose_name='user', default=None)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    first_name = models.CharField(max_length=40, unique=False, blank=False, null=False)
    last_name = models.CharField(max_length=40, unique=False, blank=False, null=False)
    phone_number = PhoneNumberField(unique=False ,blank=False, null=False)
    email = models.EmailField(unique=False ,blank=False, null=False)
    delivery_method = models.CharField(max_length=20, unique=False, null=False, blank=False, choices=delivery_choises)
    payment_method = models.CharField(max_length=20, unique=False, null=False, blank=False, choices=payment_choises)
    locker_company = models.CharField(max_length=30, unique=False, null=True, blank=True, choices=company_locker_choises)
    locker = models.CharField(max_length=25, unique=False, blank=True, null=True)
    status = models.CharField(max_length=25, null=False, blank=False, default="In process...")
    price = models.DecimalField(max_digits=10, decimal_places = 2)
    shipment_requested = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'uzsakymas'
        verbose_name = 'uzsakymas'
        verbose_name_plural = 'uzsakymas'

    def __str__(self):
        if self.user:
            return f'Užsakymas Nº {self.pk} | Klientas {self.user.first_name} {self.user.last_name}'
        return f'Užsakymas Nº {self.pk} | Klientas anonimas'
    
    def phone_number_e164(self):
        return self.phone_number.as_e164
    
    def get_fullname(self):
        return f"{self.first_name} {self.last_name}"
    
    def recalculate_price(self):
        total = Decimal("0.00")

        for item in self.orderitem_set.all():
            total += item.price * item.quantity

        self.price = total
        self.save(update_fields=["price"])
    
    def total_price(self):
        delivery_price = Decimal("3.50")

        if self.delivery_method == "parcel":
            return self.price + delivery_price

        return self.price

class OrderItem(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE,)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    price = models.DecimalField(max_digits=10,decimal_places = 2)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    name = models.CharField(blank=False, null=False)

    class Meta:
        db_table = 'uzsakymo prekiai'
        verbose_name = 'uzsakymo prekiai'
        verbose_name_plural = 'uzsakymo prekiai'
    
    def products_price(self):
        return round(self.product.price_discount() * self.quantity, 2)
    
    def __str__(self):
        return f'Product {self.product.name} | Order Nº {self.order.pk}'
