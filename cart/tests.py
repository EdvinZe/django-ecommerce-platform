from django.test import TestCase
from products.models import Product, Category
from cart.models import Cart
from django.urls import reverse
from unittest.mock import patch


class CartModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Test")

        self.product1 = Product.objects.create(
            category=self.category,
            name="Product 1",
            price=100,
            discount=0,
            short_description="short",
            long_description="long",
            quantity=10,
            image="test.jpg"
        )

        self.product2 = Product.objects.create(
            category=self.category,
            name="Product 2",
            price=50,
            discount=0,
            short_description="short",
            long_description="long",
            quantity=10,
            image="test.jpg"
        )

    def test_products_price(self):
        cart = Cart.objects.create(product=self.product1, quantity=2)

        self.assertEqual(cart.products_price(), 200)

    def test_products_price_with_discount(self):
        self.product1.discount = 10
        self.product1.save()

        cart = Cart.objects.create(product=self.product1, quantity=2)

        self.assertEqual(cart.products_price(), 180)

    def test_total_price(self):
        Cart.objects.create(product=self.product1, quantity=2)  # 200
        Cart.objects.create(product=self.product2, quantity=1)  # 50

        carts = Cart.objects.all()

        self.assertEqual(carts.total_price(), 250)

    def test_total_quantity(self):
        Cart.objects.create(product=self.product1, quantity=2)
        Cart.objects.create(product=self.product2, quantity=3)

        carts = Cart.objects.all()

        self.assertEqual(carts.total_quantity(), 5)

    def test_total_quantity_empty(self):
        carts = Cart.objects.all()

        self.assertEqual(carts.total_quantity(), 0)

class CartViewTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Test")

        self.product = Product.objects.create(
            category=self.category,
            name="Product",
            price=100,
            short_description="short",
            long_description="long",
            quantity=10,
            image="test.jpg"
        )

        session = self.client.session
        session.save()
        self.session_key = session.session_key

    def test_cart_add_creates_cart(self):
        response = self.client.post(
            reverse("cart_add"),
            {"product_id": self.product.id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cart.objects.count(), 1)


    def test_cart_add_increases_quantity(self):
        Cart.objects.create(
            product=self.product,
            quantity=1,
            session_key=self.session_key
        )

        self.client.post(
            reverse("cart_add"),
            {"product_id": self.product.id}
        )

        cart = Cart.objects.first()

        self.assertEqual(cart.quantity, 2)

    def test_cart_add_product_not_found(self):
        response = self.client.post(
            reverse("cart_add"),
            {"product_id": 999}
        )

        self.assertEqual(response.json()["success"], False)

    @patch("cart.views.can_add_product_to_cart")
    def test_cart_add_out_of_stock(self, mock_can_add):
        mock_can_add.return_value = False

        response = self.client.post(
            reverse("cart_add"),
            {"product_id": self.product.id}
        )

        self.assertEqual(response.json()["success"], False)

    
    def test_cart_remove(self):
        cart = Cart.objects.create(product=self.product, quantity=2)

        response = self.client.post(
            reverse("cart_remove"),
            {"cart_id": cart.id}
        )

        self.assertEqual(Cart.objects.count(), 0)


    def test_cart_change_quantity(self):
        cart = Cart.objects.create(product=self.product, quantity=1)

        response = self.client.post(
            reverse("cart_change"),
            {"cart_id": cart.id, "quantity": 5}
        )

        cart.refresh_from_db()

        self.assertEqual(cart.quantity, 5)


    def test_cart_change_invalid_quantity(self):
        cart = Cart.objects.create(
            product=self.product,
            quantity=1,
            session_key=self.session_key
        )

        response = self.client.post(
            reverse("cart_change"),
            {"cart_id": cart.id, "quantity": "abc"}
        )

        data = response.json()

        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Invalid quantity")


    def test_cart_change_valid(self):
        cart = Cart.objects.create(
            product=self.product,
            quantity=1,
            session_key=self.session_key
        )

        self.client.post(
            reverse("cart_change"),
            {"cart_id": cart.id, "quantity": 5}
        )

        cart.refresh_from_db()

        self.assertEqual(cart.quantity, 5)