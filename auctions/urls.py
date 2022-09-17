from django.urls import path

from . import views

app_name = "commerce"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new, name="new"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.category, name="category"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("bid/<int:listing_id>", views.bid, name="bid")
]
