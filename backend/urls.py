from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf.urls.static import static
from django.conf import settings
import debug_toolbar
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('', include('products.urls')),
    path('users/', include('users.urls')),
    path('password_reset/', include('pass_change.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('lockers/', include('lockers.urls')),
    path('api/', include('api.urls')),
    path('manager/', include('manager.urls')),
    # path("__debug__/", include(debug_toolbar.urls)),
    path('payments/', include('payments.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT
    }),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
handler404 = "core.errors.views.error_404"
handler500 = "core.errors.views.error_500"
handler403 = "core.errors.views.error_403"