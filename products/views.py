from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Subcategory, ProductImage
from django.db.models import Q, F, FloatField
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from .forms import ProductForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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
    return render(request, "products/list.html", context)


@login_required
def create_view(request):
    product_form = ProductForm()

    if request.method == "POST":
        product_form = ProductForm(request.POST or None)
        images = request.FILES.getlist("image", None)
        subcategory = request.POST.get("subcategory")

        if product_form.is_valid() and images:
            new_product = product_form.save(commit=False)
            new_product.user = request.user
            new_product.subcategory = get_object_or_404(Subcategory, id=int(subcategory))
            new_product.save()

            for image in images:
                ProductImage.objects.create(
                    product=new_product, image=image
                )

            return redirect("products:index")
        else:
            print(product_form.errors)

    context = {
        "product_form": product_form,
    }
    return render(request, "products/create.html", context)


def load_subcategories(request):
    data = {}
    category = request.POST.get("category", None)
    if category:
        subcategories = Subcategory.objects.filter(category__id=int(category))

        data = [{"id": subcategory.id, "name": subcategory.name} for subcategory in subcategories]
    return JsonResponse({"subcategories": data})