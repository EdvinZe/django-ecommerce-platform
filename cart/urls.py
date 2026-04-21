from django.urls import path
from cart.views import cart_add, cart_change, cart_remove, users_cart


urlpatterns = [
    path('cart_add/', cart_add, name='cart_add'),
    path('cart_change/', cart_change, name='cart_change'),
    path('cart_remove/', cart_remove, name='cart_remove'),
    path('users_cart/', users_cart, name='users_cart')
]
