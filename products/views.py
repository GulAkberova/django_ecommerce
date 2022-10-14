from django.shortcuts import render
from .models import Product, Category
from django.db.models import Q, F, FloatField
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
# Create your views here.


def index_view(request):
    context = {}
    search = request.GET.get("search", None)
    min_price = request.GET.get("min_price", None)
    max_price = request.GET.get("max_price", None)
    subcategory = request.GET.get("subcategory", None)

    products = Product.objects.annotate(
        tax_float_price = Coalesce("tax_price", 0, output_field=FloatField())
    ).annotate(
        discount_float_price = Coalesce("discount_price", 0, output_field=FloatField())
    ).annotate(
        total_price=F("price") + F("tax_float_price") - F("discount_float_price")
    ).order_by("-created_at")

    categories = Category.objects.order_by("-created_at")

    if search:
        products = products.filter(
            Q(name__icontains=search)|
            Q(description__icontains=search)
        )
        context["search"] = search


    if min_price or max_price:
        if min_price:
            products = products.filter(
                total_price__gte=float(min_price)
            )
            context["min_price"] = min_price

        if max_price:
            products = products.filter(
                total_price__lte=float(max_price)
            )
            context["max_price"] = max_price

    if subcategory:
        products = products.filter(
            subcategory__id=int(subcategory)
        )
        context["selected_subcategory"] = int(subcategory)

    paginator = Paginator(products, 2)
    page = request.GET.get('page', 1)
    product_list = paginator.get_page(page)


    context["products"] = product_list
    context["paginator"] = paginator
    context["categories"] = categories
    return render(request, "index.html", context)