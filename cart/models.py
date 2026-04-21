from django.db import models
from users.models import User
from products.models import Product
from django.db.models import Sum

class CartQuerySet(models.QuerySet):
    def total_price(self):
        return sum(cart.products_price() for cart in self)
    

    def total_quantity(self):
        return self.aggregate(total=Sum("quantity"))["total"] or 0   
     

class Cart(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(default=0)
    session_key = models.CharField(null=True, blank=True)
    created_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart'
        verbose_name = 'cart'
        verbose_name_plural = 'cart'

    objects = CartQuerySet().as_manager()

    def products_price(self):
        return round(self.product.price_discount() * self.quantity, 2)
    
    def __str__(self):
        if self.user:
            return f'Cart {self.user.username} | Product {self.product.name} | Quantity {self.quantity}'
        
        return f'Anonymous cart | Product {self.product.name} | Quantity {self.quantity}'