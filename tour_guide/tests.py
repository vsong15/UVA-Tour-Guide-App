from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from django.test import SimpleTestCase
from django.contrib.auth.models import User
from django.conf import settings
from .models import Review
from django.db.models import Avg

# Test the home page elements and page status
class HomePageTests(TestCase):
    def test_home_page_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'tour_guide/home.html')

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')

    def test_user_home_page_status_code(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_home'))
        self.assertEqual(response.status_code, 200)

    def test_user_home_template_contains_elements(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_home'))
        self.assertContains(response, 'Welcome User,')
        self.assertContains(response, 'Account Name:')
        self.assertContains(response, 'Logout')
        self.assertContains(response, 'id="start"')
        self.assertContains(response, 'id="end"')
        self.assertContains(response, 'id="get-route"')
        self.assertContains(response, 'id="location-search"')
        self.assertContains(response, 'id="category-search"')
        self.assertContains(response, 'id="map"')
        self.assertContains(response, 'https://maps.googleapis.com/maps/api/js?key={}&callback=initMap&libraries=places"'.format(settings.GOOGLE_MAPS_API_KEY))

# Test the mainpage status after an user logs in
class MainPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')

    def test_main_page_status_code_for_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('mainpage'))
        self.assertEqual(response.status_code, 200)

# Test the necessary elements in the page
class TemplateTests(SimpleTestCase):
    databases = '__all__' 
    def test_home_template_contains_correct_html(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, '<h1 class="display-4">Welcome to the UVA Tour Guide App!</h1>', html=True)

    def test_user_home_template_contains_logout_link(self):
        response = self.client.get(reverse('user_home'))
        self.assertContains(response, '<a href="/accounts/logout/" class="btn btn-danger btn-sm" role="button">Logout</a>')

# Test get routes on the map on the user home page
class UserHomePageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')

    def test_user_home_page_status_code_for_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_home'))
        self.assertEqual(response.status_code, 200)

    # Valid Input
    def test_get_route_button_with_both_empty_inputs(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_home'))
        
        data = {
            'start': '',  # Empty start location
            'end': ''  # Empty end location
        }
        response = self.client.post(reverse('user_home'), data)
        self.assertEqual(response.status_code, 200)  
        self.assertContains(response, 'Directions request failed due to ')

    # Bad input
    def test_get_route_button_with_one_empty_inputs(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_home'))
        
        data = {
            'start': 'the lawn', 
            'end': ''  # Empty end location
        }
        response = self.client.post(reverse('user_home'), data)
        self.assertEqual(response.status_code, 200)  
        self.assertContains(response, 'Directions request failed due to ')

    # Another bad input
    def test_get_route_button_with_invalid_inputs(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_home'))
        data = {
            'start': 'rootunda',
            'end': 'newwcombb'
        }
        response = self.client.post(reverse('user_home'), data)
        self.assertEqual(response.status_code, 200)  
        self.assertContains(response, 'Directions request failed due to ')
    
    # Test if the fields are populated properly
    def test_user_home_page_contains_input_fields(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_home'))
        self.assertContains(response, 'id="start"')
        self.assertContains(response, 'id="end"')
        self.assertContains(response, 'id="get-route"')
        self.assertContains(response, 'id="location-search"')
        self.assertContains(response, 'id="category-search"')

    # Test user info on the page
    def test_user_home_page_contains_user_info(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_home'))
        self.assertContains(response, 'Welcome User, {} {}!'.format(self.user.first_name, self.user.last_name))
        #self.assertContains(response, 'Account Name: {}'.format(self.user.username))

    def test_user_home_page_loads_correct_js_script(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_home'))
        self.assertContains(response, 'https://maps.googleapis.com/maps/api/js?key={}&callback=initMap&libraries=places"'.format(settings.GOOGLE_MAPS_API_KEY))
    
# Test Map API for home page and user home page
class HomePageGoogleMapsAPITests(TestCase):
    def test_home_page_contains_google_maps_api_key(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, f'https://maps.googleapis.com/maps/api/js?key={settings.GOOGLE_MAPS_API_KEY}')


class UserHomePageGoogleMapsAPITests(TestCase):
    def test_user_home_page_contains_google_maps_api_key(self):
        response = self.client.get(reverse('user_home'))
        self.assertContains(response, f'https://maps.googleapis.com/maps/api/js?key={settings.GOOGLE_MAPS_API_KEY}')

# Test add a pending review to see if it can be viewed at admin page and admin can approve it
class AdminReviewApprovalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpassword', is_staff=True)
        self.client.login(username='testuser', password='testpassword')
        
    def submit_review(self):
        # Simulate a valid review submission
        return self.client.post(reverse('submit_review'), {
            'location': 'Newcomb Hall, McCormick Road, Charlottesville, VA, USA',
            'rating': 5,
            'comments': 'Test Comment'
        })

    def test_submit_review(self):
        # Verify that a review object is created for the user
        response = self.submit_review()
        self.assertTrue(Review.objects.filter(user=self.user).exists())

        self.assertEqual(Review.objects.count(), 1)

        created_review = Review.objects.first()
        self.assertEqual(created_review.location, 'Newcomb Hall, McCormick Road, Charlottesville, VA, USA')
        self.assertEqual(created_review.rating, 5)
        self.assertEqual(created_review.comments, 'Test Comment')
        self.assertContains(response, 'Review submitted successfully!')


    def test_verify_review(self):
        self.submit_review()
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('admin_home'))
        self.assertIn(self.user.review_set.first(), response.context['unverified_reviews'])
        unverified_review = self.user.review_set.first()
        # Approve the request
        response = self.client.post(reverse('verify_review', args=[unverified_review.id]), {'action': 'approve'})
        verified_review = Review.objects.get(pk=unverified_review.id)
        self.assertTrue(verified_review.verified)
        self.assertIn(verified_review, response.context['verified_reviews'])

        # Check if the review is removed from unverified_reviews queryset after approval
        response = self.client.get(reverse('admin_home'))
        self.assertNotIn(verified_review, response.context['unverified_reviews'])
        
# Test add a pending review to see if it can be viewed at admin page and admin can deny it
class AdminReviewDenyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpassword', is_staff=True)
        self.client.login(username='testuser', password='testpassword')
        
        # Simulate a valid review submission
        response = self.client.post(reverse('submit_review'), {
            'location': 'The Rotunda',
            'rating': 2,
            'comments': 'Test?'
        })

    def test_submit_review(self):
        # Verify that a review object is created for the user
        self.assertTrue(Review.objects.filter(user=self.user).exists())

        self.assertEqual(Review.objects.count(), 1)

        created_review = Review.objects.first()
        self.assertEqual(created_review.location, 'The Rotunda')
        self.assertEqual(created_review.rating, 2)
        self.assertEqual(created_review.comments, 'Test?')

    def test_deny_review(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('admin_home'))
        unverified_review = self.user.review_set.first()
        self.assertIn(unverified_review, response.context['unverified_reviews'])
        # Deny the review
        response = self.client.post(reverse('verify_review', args=[unverified_review.id]), {'action': 'deny'})
        
        # Verify that the review is deleted from the database after denial
        with self.assertRaises(Review.DoesNotExist):
            denied_review = Review.objects.get(pk=unverified_review.id)

        response = self.client.get(reverse('admin_home'))
        self.assertNotIn(unverified_review, response.context['unverified_reviews'])
        self.assertContains(response, 'There are no verified reviews at the moment.')

# Test to see the sign out notification for regular user
class SignOutNotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_sign_out_notification(self):
        self.client.login(username='testuser', password='testpassword')

        self.assertTrue(self.client.session['_auth_user_id'])
        response = self.client.get(reverse('account_logout'), follow=True)
        self.assertNotIn('_auth_user_id', self.client.session)

        # Check if the sign-out notification is present in the response
        self.assertContains(response, 'You have signed out.')

# Test to see the sign out notification for admin user
class SignOutNotificationAdminTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpassword', is_staff=True)

    def test_sign_out_admin_notification(self):
        self.client.login(username='adminuser', password='adminpassword')

        self.assertTrue(self.client.session['_auth_user_id'])
        response = self.client.get(reverse('account_logout'), follow=True)
        self.assertNotIn('_auth_user_id', self.client.session)

        # Check if the sign-out notification is present in the response
        self.assertContains(response, 'You have signed out.')

# Test to see if Popular locations work with: 1. right order, 2. right passing bar
class PopularLocationsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpassword', is_staff=True)
        self.client.login(username='adminuser', password='adminpassword')

    def submit_review(self, location, rating, comments):
        return self.client.post(reverse('submit_review'), {
            'location': location,
            'rating': rating,
            'comments': comments
        })

    def approve_reviews(self):
        # Log in as admin user and approve reviews
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('admin_home'))
        unverified_reviews = response.context['unverified_reviews']

        # Approve the request
        for review in unverified_reviews:
            response = self.client.post(reverse('verify_review', args=[review.id]), {'action': 'approve'})

        # Check if all reviews are now in the verified_reviews context
        verified_reviews = response.context['verified_reviews']

        # Check if all reviews are marked as verified in the database
        for review in verified_reviews:
            verified_review = Review.objects.get(pk=review.id)
            self.assertTrue(verified_review.verified)


    def test_popular_locations(self):
        # Step 1: Log in as a regular user and add reviews to "Rice Hall" and "The Rotunda" with high ratings
        self.client.login(username='testuser', password='testpassword')
        self.submit_review('Rice Hall, Engineer\'s Way, Charlottesville, VA, USA', 4, 'Good place')
        self.submit_review('Rice Hall, Engineer\'s Way, Charlottesville, VA, USA', 5, 'W place')
        self.submit_review('The Rotunda', 5, 'Amazing architecture')
        self.submit_review('The Rotunda', 5, 'Historical landmark')

        # Step 2: add bad reviews to "newComb"
        self.submit_review('NewComb', 1, 'bad!!')
        self.submit_review('NewComb', 2, 'worst food on campus')

        # Step 3: Log in as an admin user and approve reviews
        self.approve_reviews()

        # Step 4: Log out
        self.client.logout()

        # Step 5: Log in as a regular user and check if locations appear in "Popular Locations"
        self.client.login(username='testuser', password='testpassword')

        # Check the highest-rated locations
        highest_rated_locations = (
            Review.objects.values('location')
            .annotate(avg_rating=Avg('rating'))
            .filter(avg_rating__gte=4)
            .order_by('-avg_rating')[:10]
        )

        # Make sure low ratings will not be revealed in "Popular Locations"
        expected_locations = [
            {'name': 'The Rotunda', 'avg_rating': 5.0},
            {'name': 'Rice Hall, Engineer\'s Way, Charlottesville, VA, USA', 'avg_rating': 4.5},
        ]

        # Check if the locations are in the correct order with correct average ratings
        self.assertEqual(len(highest_rated_locations), len(expected_locations))

        for i, expected_location in enumerate(expected_locations):
            actual_location = highest_rated_locations[i]['location']
            actual_avg_rating = highest_rated_locations[i]['avg_rating']

            self.assertEqual(actual_location, expected_location['name'])
            self.assertAlmostEqual(actual_avg_rating, expected_location['avg_rating'])

# Test to edit and delete a review
class AdminReviewActionsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='adminuser', password='adminpassword', is_staff=True)
        self.client.login(username='adminuser', password='adminpassword')
        
    def create_review(self, location, rating, comments, verified=False):
        return Review.objects.create(location=location, rating=rating, comments=comments, user=self.user, verified=verified)

    def test_delete_review(self):
        # Create a review to delete
        review = self.create_review('Test Location', 4, 'Test Comment', verified=False)

        # Delete the review
        response = self.client.post(reverse('delete_review', args=[review.id]))

        # Check if the review is deleted successfully
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(review, Review.objects.all())
        self.assertContains(response, 'Review deleted successfully!')

    def test_edit_review(self):
        # Create a review to edit
        review = self.create_review('Test Location', 4, 'Test Comment', verified=False)

        # Edit the review
        new_location = 'Updated Location'
        new_rating = 5
        new_comment = 'Updated Comment'
        response = self.client.post(reverse('edit_review'), {
            'reviewId': review.id,
            'editLocation': new_location,
            'editRating': new_rating,
            'editComment': new_comment,
        })

        # Check if the review is updated successfully
        self.assertEqual(response.status_code, 200)
        updated_review = Review.objects.get(pk=review.id)
        self.assertEqual(updated_review.location, new_location)
        self.assertEqual(updated_review.rating, new_rating)
        self.assertEqual(updated_review.comments, new_comment)
        self.assertContains(response, 'Review updated successfully!')

        