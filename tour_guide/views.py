from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.shortcuts import reverse
from django.conf import settings
from .forms import ReviewForm
from .models import Review
from django.db.models import Avg
from django.contrib import messages

import json
                                   
def home(request): 
    threshold_rating = 4
    highest_rated_locations = (
        Review.objects.values('location')
        .annotate(avg_rating=Avg('rating'))
        .filter(avg_rating__gte=threshold_rating)
        .order_by('-avg_rating')[:6]
    )
    locations = list(highest_rated_locations.values('location'))
    escaped_locations = [{'location': loc['location'].replace("'", "\''")} for loc in locations]
    locations_json = json.dumps(escaped_locations)
    
    return render(request, 'tour_guide/home.html', {'locations_json': locations_json, 'highest_rated_locations': highest_rated_locations, 'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY})

def mainpage(request):
    threshold_rating = 4
    highest_rated_locations = (
        Review.objects.values('location')
        .annotate(avg_rating=Avg('rating'))
        .filter(avg_rating__gte=threshold_rating)
        .order_by('-avg_rating')[:6]
    )

    most_recent_verified_review = Review.objects.filter(verified=True).order_by('-created_at').first()
    if most_recent_verified_review is not None and most_recent_verified_review.location:
        success_message = f'Most recent verified review - Location: {most_recent_verified_review.location}, Rating: {most_recent_verified_review.rating}, Comments: {most_recent_verified_review.comments}, User: {most_recent_verified_review.user}, Created At: {most_recent_verified_review.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
        messages.success(request, success_message)

    if request.method == 'POST':
        location = request.POST.get('location-reviews')
        verified_reviews = Review.objects.filter(verified=True, location=location)
        tab_values = [
            request.POST.get('current_tab1'),
            request.POST.get('current_tab2'),
        ]
        selected_tab = next((tab for tab in tab_values if tab), None)
        if selected_tab == "#location-reviews-tab":
            context = {
                'verified_reviews': verified_reviews,
                'location': location,
                'highest_rated_locations': highest_rated_locations,
                'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
                'selected_tab': selected_tab,
            }
            return render(request, 'tour_guide/user_home.html', context)
        elif selected_tab == "#add-review":
            form = ReviewForm(request.POST)
            context = {
                'verified_reviews': verified_reviews,
                'location': location,
                'highest_rated_locations': highest_rated_locations,
                'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
                'form': form,
                'selected_tab': selected_tab,
            }
            if form.is_valid():
                Review.objects.create(
                    location=form.cleaned_data['location'],
                    rating=form.cleaned_data['rating'],
                    comments=form.cleaned_data['comments'],
                    user=request.user
                )
                messages.success(request, 'Review submitted successfully!')
                return render(request, 'tour_guide/user_home.html', context)
            else:
                messages.error(request, 'Failed to submit review. Please check the form for errors.')
                return render(request, 'tour_guide/user_home.html', context)

        print(selected_tab)
        print(request.POST)
        
    if request.user.is_staff or request.user.is_superuser or request.user.email == "cs3240.super@gmail.com" or request.user.email == "ng7zw@virginia.edu": 
        return redirect('admin_home')
    return render(request, 'tour_guide/user_home.html', {'highest_rated_locations': highest_rated_locations, 'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY})

def admin_home(request):
    if not (request.user.is_staff or request.user.email == "cs3240.super@gmail.com" or request.user.email == "ng7zw@virginia.edu"):
        return redirect('home_page')
    unverified_reviews = Review.objects.filter(verified=False)
    verified_reviews = Review.objects.filter(verified=True)
    context = {
        'unverified_reviews': unverified_reviews,
        'verified_reviews': verified_reviews,   
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'tour_guide/admin_home.html', context)


def user_home(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            location = request.POST.get('location')
            verified_reviews = Review.objects.filter(verified=True, location=location)
            context = {
                'form': form, 
                'verified_review': verified_reviews,
                'location': location,
                'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
            }
            return render(request, 'tour_guide/user_home.html', context)
    else:
        form = ReviewForm()
    return render(request, 'tour_guide/user_home.html', {'form': form, 'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY})

def submit_review(request):
    threshold_rating = 4
    highest_rated_locations = (
        Review.objects.values('location')
        .annotate(avg_rating=Avg('rating'))
        .filter(avg_rating__gte=threshold_rating)
        .order_by('-avg_rating')[:6]
    )
    verified_reviews = Review.objects.filter(verified=True)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.create(
                location=form.cleaned_data['location'],
                rating=form.cleaned_data['rating'],
                comments=form.cleaned_data['comments'],
                user=request.user
            )  
            messages.success(request, 'Review submitted successfully!')
            context = {
                'form': form, 'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
                'verified_reviews': verified_reviews,
                'highest_rated_locations': highest_rated_locations,
                'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
            }
            return render(request, 'tour_guide/user_home.html', context)
    else:
        form = ReviewForm()
    context = {
        'form': form, 'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
        'verified_reviews': verified_reviews,
        'highest_rated_locations': highest_rated_locations,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, 'tour_guide/user_home.html', context)


def verify_review(request, review_id):
    if request.method == 'POST' and request.user.is_staff:
        review = get_object_or_404(Review, pk=review_id)
        if request.POST.get("action") == "deny":
            review.delete()
        else:
            review.verified = True
            review.save()
        if not (request.user.is_staff or request.user.email == "cs3240.super@gmail.com" or request.user.email == "ng7zw@virginia.edu"):
            return redirect('home_page')
        unverified_reviews = Review.objects.filter(verified=False)
        verified_reviews = Review.objects.filter(verified=True)
        context = {
            'unverified_reviews': unverified_reviews,
            'verified_reviews': verified_reviews,
            'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, 'tour_guide/admin_home.html', context)
    
def delete_review(request, review_id):
    unverified_reviews = Review.objects.filter(verified=False)
    verified_reviews = Review.objects.filter(verified=True)
    context = {
        'unverified_reviews': unverified_reviews,
        'verified_reviews': verified_reviews,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    }
    if request.method == 'POST':
        review = get_object_or_404(Review, pk=review_id)
        review.delete()
        messages.success(request, 'Review deleted successfully!')
        return render(request, 'tour_guide/admin_home.html', context)
    return render(request, 'tour_guide/admin_home.html', context)

def edit_review(request):
    if request.method == 'POST':
        review_id = request.POST.get('reviewId')
        review = get_object_or_404(Review, pk=review_id)
        new_location = request.POST.get('editLocation')
        new_rating = request.POST.get('editRating')
        new_comment = request.POST.get('editComment')
        if new_location:
            review.location = new_location
        if new_rating:
            review.rating = new_rating
        if new_comment:
            review.comments = new_comment

        review.save()
        messages.success(request, 'Review updated successfully!')
        unverified_reviews = Review.objects.filter(verified=False)
        verified_reviews = Review.objects.filter(verified=True)
        context = {
            'unverified_reviews': unverified_reviews,
            'verified_reviews': verified_reviews,
            'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, 'tour_guide/admin_home.html', context)
   
    unverified_reviews = Review.objects.filter(verified=False)
    verified_reviews = Review.objects.filter(verified=True)
    context = {
        'unverified_reviews': unverified_reviews,
        'verified_reviews': verified_reviews,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'tour_guide/admin_home.html', context)