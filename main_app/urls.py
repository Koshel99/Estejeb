# main_app/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # Login & Logout URLs
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/signup/', views.signup, name='signup'),
    
    #Organization URLS
    path('organizations/<int:id>/', views.organization_profile, name='organization-profile'),
    path('organizations/create/', views.OrganizationCreate.as_view(), name='organization-create'),
    path('organizations/<int:pk>/edit/', views.OrganizationUpdate.as_view(), name='organization-edit'),
    path('organizations/<int:pk>/delete/', views.OrganizationDelete.as_view(), name='organization-delete'),
]
