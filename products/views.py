from django.db.models import Case, When
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from cart.utils import get_users_carts
from products.services import get_catalog_ids, get_categories, get_main_products, get_product, get_related_products
from .models import Product, Category
from .utils import search_q
import logging

logger = logging.getLogger(__name__)

class MainView(TemplateView):
    template_name = 'products/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = "Pagrindinys puslapis"
        context["products"] = get_main_products()

        return context

class CatalogView(ListView):
    model = Product
    template_name = 'products/catalog.html'
    context_object_name = 'products'
    paginate_by = 4
    allow_empty = True

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        on_sale = self.request.GET.get('on_sale')
        order_by = self.request.GET.get('order_by')
        query = self.request.GET.get('q')
        page = self.request.GET.get("page", 1)

        ids = get_catalog_ids(
        category_slug, on_sale, order_by, query, page
    )

        if not ids:
            if query:
                logger.info(f"[AUDIT] Catalog search empty query='{query}'")
            return Product.objects.none()

        preserved_order = Case(
            *[When(id=pk, then=pos) for pos, pk in enumerate(ids)]
        )

        return Product.objects.filter(id__in=ids).order_by(preserved_order)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Katalogas'
        context['slug_url'] = self.kwargs.get('category_slug')
        context['categories'] = get_categories()
        return context

class ProductView(DetailView):
    template_name = 'products/product.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'
    slug_field = 'slug'
    
    def get_object(self, queryset=None):
        slug = self.kwargs.get('product_slug')

        product = get_product(slug)

        if not product:
            logger.warning(f"[AUDIT] Product not found slug={slug}")
            raise Http404("Product not found")

        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = self.object.name
        context['related_products'] = get_related_products(self.object.id)

        return context
    