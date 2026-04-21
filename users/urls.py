from django.urls import path
from users.views import registration, login, logout, profile, MyPasswordChangeView

urlpatterns = [
    path('registration/', registration, name='registration'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('change_password/', MyPasswordChangeView.as_view(), name='change_password')
]
