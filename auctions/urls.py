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
    path("watchlist/<int:listing_id>", views.toggle_watchlist, name="toggle_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("comment/<int:listing_id>", views.add_comment, name="add_comment"),
    path("close_auction/<int:listing_id>", views.close_listing, name="close_listing")
]
