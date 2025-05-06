# main_app/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # General
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # Auth
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/signup/', views.signup, name='signup'),

    # Organizations
    path('organizations/', views.organization_list, name='organization-list'),
    path('organizations/<int:id>/', views.organization_profile, name='organization-profile'),
    path('organizations/create/', views.create_organization, name='organization-create'),
    path('organizations/<int:pk>/edit/', views.OrganizationUpdate.as_view(), name='organization-edit'),
    path('organizations/<int:pk>/delete/', views.OrganizationDelete.as_view(), name='organization-delete'),
    path('opportunities/<int:opportunity_id>/thank-you/', views.thank_you_for_applying, name='thank-you-for-applying'),


    # Volunteer
    path('volunteer/profile/<int:id>/', views.volunteer_profile, name='volunteer-profile'),
    path('volunteers/', views.view_all_volunteers, name='view_all_volunteers'),
    path('volunteer/profile/<int:id>/edit/', views.volunteer_edit, name='volunteer-edit'),
    path('volunteer/profile/<int:id>/delete/', views.volunteer_delete, name='volunteer-delete'),

    # Opportunities (Causes)
    path('opportunities/', views.opportunity_list, name='opportunity-list'),
    path('opportunities/create/', views.create_opportunity, name='opportunity-create'),
    path('opportunities/<int:id>/', views.opportunity_detail, name='opportunity-detail'),
    path('opportunities/<int:id>/applicants/', views.applicants_list, name='applicants-list'),
    path('opportunities/<int:id>/apply/', views.apply_to_opportunity, name='apply-opportunity'),
    path('opportunity/<int:id>/mark-as-filled/', views.mark_as_filled, name='mark-as-filled'),
    path('opportunities/<int:pk>/edit/', views.OpportunityUpdate.as_view(), name='opportunity-edit'),
    path('opportunities/<int:pk>/delete/', views.OpportunityDelete.as_view(), name='opportunity-delete'),
]