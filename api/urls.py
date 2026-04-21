from django.urls import include, path
from api.views import DeleteSubscription, ManagerMarkPacked, ManagerOrdersView, PushSubscriptionStatus, SaveSubscription

urlpatterns = [
    path("", ManagerOrdersView.as_view(), name="api"),
    path("<int:order_id>/packed/", ManagerMarkPacked.as_view()),
    path("push/subscribe/", SaveSubscription.as_view()),
    path("push/unsubscribe/", DeleteSubscription.as_view(), name="push_unsubscribe"),
    path("push/status/", PushSubscriptionStatus.as_view(), name="push_status"),
    
]
