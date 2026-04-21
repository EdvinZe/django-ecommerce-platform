from cart.utils import get_users_carts
from orders.models import Order

def carts(request):
    return {"carts": get_users_carts(request)}
