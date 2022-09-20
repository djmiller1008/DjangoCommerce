
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Category, Listing, User, Bid, Watchlist, Comment


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
            if 'category' not in request.POST:
                category = Category.objects.get(name='None')
            else:
                category = Category.objects.get(name=request.POST['category'])
            user = request.user
            new_listing = Listing(title=title,
                                    description=description,
                                    starting_bid=starting_bid,
                                    current_bid=starting_bid,
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
    listing = Listing.objects.get(pk=id)
    winner = False
    if listing.closed:
        winning_user = listing.bids.latest('amount').user
        if request.user == winning_user:
            winner = True


        return render(request, "auctions/closed_listing.html", {
            "listing": listing,
            "winner": winner,
            "winning_user": winning_user
        })



    listing_user = listing.user
    bids_no = listing.bids.count()
    comment_form = NewCommentForm()
    category = listing.category
    comments = listing.comments.all()
    close_auction = False
    not_signed_in = False

    if request.user == listing.user:
        close_auction = True

    if request.user not in User.objects.all():
        watchlist = ''
        not_signed_in = True
    else: 
        watchlist_item = request.user.watchlist.filter(listing=listing)

        
        if not watchlist_item:
            watchlist = 'Add To Watchlist'
        else:
            watchlist = 'Remove From Watchlist'

    if request.method == 'POST':
        form = NewBidForm(request.POST)
        if request.user not in User.objects.all():
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "form": NewBidForm(),
                "listing_user": listing_user, 
                "bids": bids_no,
                "category": category,
                "bidding_user": request.user, 
                "message": "You must be signed in to bid on a listing",
                "watchlist": watchlist,
                "comment_form": comment_form,
                "comments": comments,
                "close_auction": close_auction,
                "not_signed_in": not_signed_in
            })

        if form.is_valid():
            amount = form.cleaned_data['amount']
            listing = Listing.objects.get(pk=id)

            if amount <= listing.current_bid and bids_no > 0:
               
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "form": NewBidForm(),
                    "listing_user": listing_user, 
                    "bids": bids_no,
                    "category": category,
                    "bidding_user": request.user, 
                    "message": "Your bid must be higher than the current bid",
                    "watchlist": watchlist,
                    "comment_form": comment_form,
                    "comments": comments,
                    "close_auction": close_auction,
                    "not_signed_in": not_signed_in
                })
            
            elif amount < listing.current_bid:
                
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "form": NewBidForm(),
                    "listing_user": listing_user, 
                    "bids": bids_no,
                    "category": category,
                    "bidding_user": request.user, 
                    "message": "Your bid must be higher than the original price",
                    "watchlist": watchlist,
                    "comment_form": comment_form,
                    "comments": comments,
                    "close_auction": close_auction,
                    "not_signed_in": not_signed_in
                })

            listing.current_bid = amount
            listing.save()
            user = request.user
            
            new_bid = Bid(amount=amount,
                            user=user,
                            listing=listing)
            new_bid.save()
            bids_no = listing.bids.count()

            if bids_no > 0:
                bidding_user = listing.bids.latest('amount').user
                if bidding_user == request.user:
                    bidding_user = "You have the highest bid"
            else:
                bidding_user = "No bidder yet"

            return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "form": NewBidForm(),
                    "listing_user": listing_user, 
                    "bids": bids_no,
                    "category": category,
                    "bidding_user": bidding_user,
                    "watchlist": watchlist,
                    "comment_form": comment_form,
                    "comments": comments,
                    "close_auction": close_auction,
                    "not_signed_in": not_signed_in
                })

    if bids_no > 0:
        bidding_user = listing.bids.latest('amount').user
        if bidding_user == request.user:
                bidding_user = "You have the highest bid"
    else:
        bidding_user = "No bidder yet"
    
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "form": NewBidForm(),
        "listing_user": listing_user, 
        "bids": bids_no,
        "category": category,
        "bidding_user": bidding_user,
        "watchlist": watchlist,
        "comment_form": comment_form,
        "comments": comments,
        "close_auction": close_auction,
        "not_signed_in": not_signed_in
    })

class NewBidForm(forms.Form):
    amount = forms.IntegerField(min_value=1, widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': "Bid"}))

    def __init__(self, *args, **kwargs):
        super(NewBidForm, self).__init__(*args, **kwargs)
        self.fields['amount'].label = ""

@login_required
def toggle_watchlist(request, listing_id):
    user = request.user
    listing = Listing.objects.get(pk=listing_id)

    watchlist_item = request.user.watchlist.filter(listing=listing)
    
    if not watchlist_item:
        watchlist_item = Watchlist(listing=listing, user=user)
        watchlist_item.save()
        return HttpResponseRedirect(reverse('commerce:listing', kwargs={'id': listing_id}))
    else:
        watchlist_item.delete()
        return HttpResponseRedirect(reverse('commerce:listing', kwargs={'id': listing_id}))

@login_required
def watchlist(request):
    watchlist_items = request.user.watchlist.all()
    listings = []
    for item in watchlist_items:
        listings.append(item.listing)

    return render(request, 'auctions/watchlist.html', {
        "listings": listings
    })

class NewCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': "form-control comment-form"}))

@login_required
def add_comment(request, listing_id):

    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    form = NewCommentForm(request.POST)
    if form.is_valid():
        new_comment = Comment(user=user, listing=listing, comment=form.cleaned_data['comment'])
        new_comment.save()
        return HttpResponseRedirect(reverse('commerce:listing', kwargs={'id': listing.id}))
    
def close_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    listing.closed = True
    listing.save()
    return HttpResponseRedirect(reverse('commerce:listing', kwargs={'id': listing.id}))
