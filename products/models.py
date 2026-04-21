from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class ProductQuerySet(models.QuerySet):
    def visible(self):
        return self.filter(is_visible=True, category__is_visible=True)

    def hidden(self):
        return self.exclude(is_visible=True, category__is_visible=True)


class Category(models.Model):
    name = models.CharField(max_length=25, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="URL")
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        db_table = "category"
        verbose_name = "category"
        verbose_name_plural = "categories"


class Product(models.Model):
    category = models.ForeignKey(to=Category, on_delete=models.PROTECT)
    name = models.CharField(max_length=25, unique=True)
    price = models.DecimalField(default=0.00, max_digits=7, decimal_places=2)
    discount = models.DecimalField(
        default=Decimal("0.00"),
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
    )
    short_description = models.CharField(max_length=50)
    long_description = models.TextField()
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="URL")
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=10, default="kg")
    image = models.ImageField(upload_to="products", blank=True, null=False)
    is_visible = models.BooleanField(default=True)
    is_service = models.BooleanField(default=False)
    

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "product"
        verbose_name_plural = "products"
        ordering = ("id",)

    def __str__(self):
        return self.name

    def display_id(self):
        return f"{self.id:5}"

    def get_absolute_url(self):
        return reverse("product_page", kwargs={"product_slug": self.slug})

    def price_discount(self):
        if self.discount:
            return round(self.price - self.price * self.discount / 100, 2)

        return self.price

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @classmethod
    def get_delivery_product(cls):
        product, _ = cls.objects.get_or_create(
            is_service=True,
            defaults={
                "name": "Pristatymas",
                "price": Decimal("3.50"),
                "discount": Decimal("0.00"),
                "short_description": "Pristatymo mokestis",
                "long_description": "Standartinis pristatymas",
                "quantity": 999,
                "unit": "vnt",
                "is_visible": False,
                "category": Category.objects.first(),
            },
        )
        return product