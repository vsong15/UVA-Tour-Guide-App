from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/', include('allauth.urls')),
    path('mainpage/', views.mainpage, name='mainpage'),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('user_home/', views.user_home, name='user_home'),
    path('submit_review/', views.submit_review, name='submit_review'),
    path('verify_review/<int:review_id>/', views.verify_review, name='verify_review'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('edit_review/', views.edit_review, name='edit_review'),    
]