import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from orders.selectors import get_user_orders
from products.models import Product
from cart.models import Cart
from cart.utils import can_add_product_to_cart, get_users_carts

logger = logging.getLogger(__name__)

def cart_change(request):
    cart_id = request.POST.get("cart_id")
    quantity = request.POST.get("quantity")

    try:
        cart = Cart.objects.get(id=cart_id)
    except Cart.DoesNotExist:
        logger.error(f"[AUDIT] Cart not found id={cart_id}")
        return JsonResponse({"success": False})

    try:
        quantity = int(quantity)
        if quantity < 1:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({
            "success": False,
            "message": "Invalid quantity"
        })

    if not can_add_product_to_cart(request, cart.product):
        logger.warning(f"[AUDIT] Cart change blocked product={cart.product.id}")
        return JsonResponse({
            "success": False,
            "message": "Sandėlyje daugiau prekių nėra",
            "quantity": quantity,
        })

    cart.quantity = quantity
    cart.save()

    users_carts = get_users_carts(request)

    cart_items_html = render_to_string(
        "cart/included_cart.html",
        {"carts": users_carts},
        request
    )

    return JsonResponse({
        "message": "Prekės kiekis pakeistas",
        "cart_items_html": cart_items_html,
        "quantity": quantity,
        "cart_count": users_carts.total_quantity(),
    })




def cart_remove(request):
    cart_id = request.POST.get("cart_id")

    try:
        cart = Cart.objects.get(id=cart_id)
    except Cart.DoesNotExist:
        logger.error(f"[AUDIT] Cart not found id={cart_id}")
        return JsonResponse({"success": False})

    quantity = cart.quantity
    cart.delete()

    users_carts = get_users_carts(request)

    cart_items_html = render_to_string("cart/included_cart.html", {"carts": users_carts}, request)

    response_data = {
        "message": "Prekė pašalinta iš krepšelio",
        "cart_items_html": cart_items_html,
        "quantity_deleted": quantity,
        "cart_count": users_carts.total_quantity(),
    }
    return JsonResponse(response_data)

def cart_add(request):
    product_id = request.POST.get("product_id")
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        logger.error(f"[AUDIT] Product not found id={product_id}")
        return JsonResponse({"success": False})

    if not can_add_product_to_cart(request, product):
        logger.warning(f"[AUDIT] Out of stock product={product.id}")
        return JsonResponse({
            "success": False,
            "message": "Sandėlyje daugiau prekių nėra",
        })

    if request.user.is_authenticated:
        carts = Cart.objects.filter(user=request.user, product=product)

        if carts.exists():
            cart=  carts.first()
            cart.quantity += 1
            cart.save()

        else:
            Cart.objects.create(user=request.user, product=product, quantity=1)

    
    else:
        carts = Cart.objects.filter(session_key=request.session.session_key, product=product)

        if carts.exists():
            cart = carts.first()
            cart.quantity += 1
            cart.save()
        
        else:
            Cart.objects.create(session_key=request.session.session_key, product=product, quantity=1)

    users_carts = get_users_carts(request)

    cart_items_html = render_to_string("cart/included_cart.html", {"carts":users_carts}, request=request)

    response_data = {
        "message": "Pridėta į krepšelį",
        "cart_items_html": cart_items_html,
        "cart_count": users_carts.total_quantity(),
    }

    return JsonResponse(response_data)


def users_cart(request):

    if request.user.is_authenticated:
        orders = get_user_orders(request)
    else:
        orders = None

    context = {'title': 'Krepšis', "orders": orders}

    return render(request, 'cart/cart.html', context)