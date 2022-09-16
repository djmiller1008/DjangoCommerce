
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Category, Listing, User


def index(request):
    return render(request, "auctions/index.html", {
        'listings': Listing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("commerce:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("commerce:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("commerce:index"))
    else:
        return render(request, "auctions/register.html")





@login_required(login_url='login') 
def new(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            starting_bid = form.cleaned_data['starting_bid']
            image = form.cleaned_data['image_url']
            category = Category.objects.get(name=request.POST['category'])
            user = request.user
            new_listing = Listing(title=title,
                                    description=description,
                                    starting_bid=starting_bid,
                                    image=image,
                                    category=category,
                                    user=user)
            new_listing.save()

            return HttpResponseRedirect(reverse("commerce:index"))
        else:
            return render(request, "auctions/new.html", {
                "message": "Invalid Submission",
                "form": NewListingForm(),
                "categories": Category.objects.all()
            })

    return render(request, "auctions/new.html", {
        "form": NewListingForm(),
        "categories": Category.objects.all()
    })


class NewListingForm(forms.Form):
    title = forms.CharField(label = 'Title', widget=forms.TextInput(attrs={'class': "form-control"}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': "form-control"}))
    starting_bid = forms.IntegerField(min_value=1, widget=forms.TextInput(attrs={'class': "form-control"}))
    image_url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
    
    
def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })

def category(request, category):

    return render(request, "auctions/category.html", {
        "category": Category.objects.get(name=category),
        "listings": Category.objects.get(name=category).listings.all()
    })

def listing(request, id):
    return render(request, "auctions/listing.html", {
        "listing": Listing.objects.get(pk=id)

    })