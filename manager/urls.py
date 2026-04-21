from django.urls import path
from manager.views import (
    manager_bulk_mark_packed,
    manager_cancel_order,
    manager_mark_completed,
    manager_mark_packed,
    manager_mark_shipped,
    manager_order_detail,
    manager_orders_list,
    manager_order_qr_view,
    manager_retry_shipment,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/qr/",
        manager_order_qr_view,
        name="manager_order_qr",
    ),
    path("orders/", manager_orders_list, name="manager_orders_list"),
    path(
        "orders/<int:order_id>/",
        manager_order_detail,
        name="manager_order_detail",
    ),
    path(
        "orders/<int:order_id>/packed/",
        manager_mark_packed,
        name="manager_mark_packed",
    ),
    path(
        "orders/<int:order_id>/shipped/",
        manager_mark_shipped,
        name="manager_mark_shipped",
    ),
    path(
        "orders/bulk/packed/",
        manager_bulk_mark_packed,
        name="manager_bulk_mark_packed",
    ),
    path(
        "orders/<int:order_id>/cancel/",
        manager_cancel_order,
        name="manager_cancel_order",
    ),
    path(
    "order/<int:order_id>/complete/",
    manager_mark_completed,
    name="manager_mark_completed",
    ),
    path(
    "orders/<int:order_id>/retry-shipping/",
    manager_retry_shipment,
    name="manager_retry_shipment",
),
]
