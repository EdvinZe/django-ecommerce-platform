from django.urls import include, path
from .views import MainView, CatalogView, ProductView


urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('catalog/<slug:category_slug>/', CatalogView.as_view(), name='catalog'),
    path('product/<slug:product_slug>/', ProductView.as_view(), name='product_page'),
    path('catalog/search/', CatalogView.as_view(), name='search'),
]