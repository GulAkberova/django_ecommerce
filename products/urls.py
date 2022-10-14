from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.index_view, name="index"),
    path("create/", views.create_view, name="create"),
    path("load/subcategories/", views.load_subcategories, name="load-subcategories"),
]