from django.test import TestCase
from django.urls import reverse
from products.models import Product, Category

class ProductModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Test category")

        self.product = Product.objects.create(
            category=self.category,
            name="Test product",
            price=100,
            discount=0,
            short_description="short",
            long_description="long",
            quantity=10,
            image="test.jpg"
        )

    def test_price_without_discount(self):
        self.assertEqual(self.product.price_discount(), 100)

    def test_price_with_discount(self):
        self.product.discount = 10
        self.product.save()

        self.assertEqual(self.product.price_discount(), 90)

    def test_price_rounding(self):
        self.product.price = 99.99
        self.product.discount = 33
        self.product.save()

        result = self.product.price_discount()

        self.assertEqual(result, round(99.99 - 99.99 * 33 / 100, 2))

    def test_slug_created(self):
        self.assertIsNotNone(self.product.slug)

    def test_slug_not_overwritten(self):
        self.product.slug = "custom-slug"
        self.product.save()

        self.assertEqual(self.product.slug, "custom-slug")

    def test_visible_products(self):
        visible_products = Product.objects.visible()

        self.assertIn(self.product, visible_products)

    def test_hidden_products(self):
        self.product.is_visible = False
        self.product.save()

        hidden_products = Product.objects.hidden()

        self.assertIn(self.product, hidden_products)

    def test_full_discount(self):
        self.product.discount = 100
        self.product.save()

        self.assertEqual(self.product.price_discount(), 0)

    def test_negative_discount(self):
        self.product.discount = -10
        self.product.save()

        result = self.product.price_discount()

        self.assertGreaterEqual(result, 0)

class ProductViewTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Test category")

        self.product = Product.objects.create(
            category=self.category,
            name="Test product",
            price=100,
            short_description="short",
            long_description="long",
            quantity=10,
            image="test.jpg"
        )

    def test_product_view_success(self):
        url = reverse("product_page", kwargs={"product_slug": self.product.slug})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["product"].id, self.product.id)

    
    def test_product_view_404(self):
        url = reverse("product_page", kwargs={"product_slug": "not-exists"})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)