from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    image = models.ImageField(upload_to='users_images', blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone = PhoneNumberField(blank=False, null=False, unique=False)
    is_manager = models.BooleanField(default=False)

    class Meta:
        db_table = 'user'
        verbose_name = 'user'
        verbose_name_plural = 'users'


    def __str__(self):
        return self.username
    