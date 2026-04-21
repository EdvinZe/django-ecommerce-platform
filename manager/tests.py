from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch

from orders.models import Order
from lockers.models import Shipment

User = get_user_model()


class ManagerViewsTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            phone="+37060000001",
            password="123",
            is_staff=True
        )

        self.user = User.objects.create_user(
            username="user",
            email="user@test.com",
            phone="+37060000002",
            password="123"
        )

        self.order = Order.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="+37060000003",
            email="order@test.com",
            delivery_method="parcel",
            payment_method="card",
            locker="123",
            locker_company="omniva",
            price=100,
            status="paid"
        )

    def test_access_requires_staff(self):
        url = reverse("manager_orders_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_staff_can_access(self):
        self.client.login(username="admin", password="123")
        url = reverse("manager_orders_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_mark_packed(self):
        self.client.login(username="admin", password="123")

        self.order.status = "shipped"
        self.order.save()

        url = reverse("manager_mark_packed", args=[self.order.id])
        self.client.post(url)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "packed")

    def test_mark_shipped_requires_shipment(self):
        self.client.login(username="admin", password="123")

        self.order.status = "packed"
        self.order.save()

        url = reverse("manager_mark_shipped", args=[self.order.id])
        self.client.post(url)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "packed")

    def test_mark_shipped_success(self):
        self.client.login(username="admin", password="123")

        self.order.status = "packed"
        self.order.save()

        Shipment.objects.create(
            order=self.order,
            provider="omniva",
            shipment_id="123",
            tracking_number="ABC"
        )

        url = reverse("manager_mark_shipped", args=[self.order.id])
        self.client.post(url)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "shipped")

    def test_mark_completed(self):
        self.client.login(username="admin", password="123")

        self.order.status = "shipped"
        self.order.save()

        url = reverse("manager_mark_completed", args=[self.order.id])
        self.client.post(url)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "completed")

    def test_cancel_order(self):
        self.client.login(username="admin", password="123")

        self.order.status = "pending"
        self.order.save()

        url = reverse("manager_cancel_order", args=[self.order.id])
        self.client.post(url)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "cancelled")

    @patch("lockers.services.send_to_carrier")
    def test_retry_shipment(self, mock_send):
        self.client.login(username="admin", password="123")

        self.order.status = "shipping_error"
        self.order.save()

        response = self.client.post(
            reverse("manager_retry_shipment", args=[self.order.id])
        )

        self.assertEqual(response.status_code, 302)