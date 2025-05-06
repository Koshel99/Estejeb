# main_app/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from .models import Organization, Opportunity, VolunteerProfile, Application
from .forms import OrganizationForm, VolunteerProfileForm, OpportunityForm

# Home Page View
def home(request):
    organizations = Organization.objects.all().order_by('-id')[:4]
    opportunities = Opportunity.objects.all().order_by('-id')[:4]
    return render(request, 'home.html', {
        'organizations': organizations,
        'opportunities': opportunities
    })

# About Page View
def about(request):
    return render(request, 'about.html')

# Admin Profile Page View (Currently redirecting to home)
def profile(request):
    return render(request, 'home.html')

# Signup View
def signup(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        organization_form = OrganizationForm(request.POST)
        volunteer_form = VolunteerProfileForm(request.POST)

        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.save()

            if 'organization' in request.POST:
                if organization_form.is_valid():
                    organization = organization_form.save(commit=False)
                    organization.user = user
                    organization.save()
            else:
                if volunteer_form.is_valid():
                    volunteer_profile = volunteer_form.save(commit=False)
                    volunteer_profile.user = user
                    volunteer_profile.save()

            login(request, user)
            return redirect('home')
    else:
        user_form = UserCreationForm()
        organization_form = OrganizationForm()
        volunteer_form = VolunteerProfileForm()

    return render(request, 'signup.html', {
        'user_form': user_form,
        'organization_form': organization_form,
        'volunteer_form': volunteer_form
    })

# Organization Profile View
@login_required
def organization_profile(request, pk):
    organization = get_object_or_404(Organization, pk=pk)
    opportunities = Opportunity.objects.filter(organization=organization, is_active=True)
    return render(request, 'organizations/organization_profile.html', {
        'organization': organization,
        'opportunities': opportunities
    })

# Organization List View
def organization_list(request):
    organizations = Organization.objects.all()
    return render(request, 'organizations/organization_list.html', {'organizations': organizations})

# Create Organization View
@login_required
def create_organization(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save(commit=False)
            organization.user = request.user
            organization.save()

            return redirect('organization-profile', id=organization.id)
        else:
            messages.error(request, 'There was an error in your form. Please check the fields and try again.')
    else:
        form = OrganizationForm()

    return render(request, 'organizations/organization_form.html', {'form': form})

# Organization CRUD Views
class OrganizationCreate(CreateView):
    model = Organization
    fields = ['name', 'description', 'location', 'website']
    template_name = 'organizations/organization_form.html'
    success_url = reverse_lazy('home')

class OrganizationUpdate(UpdateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'organizations/organization_form.html'
    success_url = reverse_lazy('home')

class OrganizationDelete(DeleteView):
    model = Organization
    template_name = 'organizations/organization_confirm_delete.html'
    success_url = reverse_lazy('home')

# Organization Details View (For admins and owners)
@login_required
def organization_details(request, id):
    organization = get_object_or_404(Organization, id=id)
    is_owner_or_superuser = (organization.user == request.user or request.user.is_superuser)
    opportunities = organization.opportunity_set.all()

    return render(request, 'organizations/organization_details.html', {
        'organization': organization,
        'is_owner_or_superuser': is_owner_or_superuser,
        'opportunities': opportunities,
    })

# Volunteer Profile View
@login_required
def volunteer_profile(request, pk):
    volunteer_profile = get_object_or_404(VolunteerProfile, pk=pk)
    
    return render(request, 'volunteers/volunteer_profile.html', {
        'volunteer_profile': volunteer_profile
    })

# View All Volunteers
def view_all_volunteers(request):
    volunteers = VolunteerProfile.objects.all()
    return render(request, 'volunteers/view_all_volunteers.html', {'volunteers': volunteers})

# Edit Volunteer Profile
@login_required
def volunteer_edit(request, id):
    volunteer_profile = get_object_or_404(VolunteerProfile, id=id)

    if request.user != volunteer_profile.user:
        return redirect('home')

    if request.method == 'POST':
        volunteer_profile.user.first_name = request.POST.get('first_name')
        volunteer_profile.user.last_name = request.POST.get('last_name')
        volunteer_profile.user.email = request.POST.get('email')
        volunteer_profile.user.save()

        form = VolunteerProfileForm(request.POST, request.FILES, instance=volunteer_profile)
        if form.is_valid():
            form.save()
            return redirect('volunteer-profile', pk=volunteer_profile.id)
    else:
        form = VolunteerProfileForm(instance=volunteer_profile)

    return render(request, 'volunteers/volunteer_edit.html', {'volunteer_profile': volunteer_profile})
    
# Delete Volunteer Profile
@login_required
@require_POST
def volunteer_delete(request, id):
    volunteer_profile = get_object_or_404(VolunteerProfile, id=id)

    if request.user != volunteer_profile.user:
        return redirect('home')

    volunteer_profile.delete()
    return redirect('signup')

# Apply to Opportunity
@login_required
def apply_to_opportunity(request, id):
    opportunity = get_object_or_404(Opportunity, id=id)
    volunteer_profile = VolunteerProfile.objects.filter(user=request.user).first()

    if not volunteer_profile:
        return redirect('create_volunteer_profile')

    if Application.objects.filter(volunteer=volunteer_profile, opportunity=opportunity).exists():
        return render(request, 'opportunities/already_applied.html')

    Application.objects.create(volunteer=volunteer_profile, opportunity=opportunity, user=request.user)

    return redirect('thank-you-for-applying', opportunity_id=id)

# Opportunity List View
def opportunity_list(request):
    opportunities = Opportunity.objects.all()
    return render(request, 'opportunities/opportunity_list.html', {'opportunities': opportunities})

# Create Opportunity View
@login_required
def create_opportunity(request):
    if request.method == 'POST':
        form = OpportunityForm(request.POST, user=request.user)
        if form.is_valid():
            opportunity = form.save(commit=False)

            if request.user.is_superuser:
                organization_id = request.POST.get('organization')
                if organization_id:
                    opportunity.organization = Organization.objects.get(id=organization_id)
                else:
                    return redirect('organization-list')
            elif hasattr(request.user, 'organization'):
                opportunity.organization = request.user.organization
            else:
                return redirect('organization-list')

            opportunity.save()
            return redirect('opportunity-list')
        else:
            messages.error(request, 'There was an issue with your form submission. Please try again.')
    else:
        form = OpportunityForm(user=request.user)

    return render(request, 'opportunities/create_opportunity.html', {'form': form})

# Opportunity Detail View
def opportunity_detail(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)

    applicants_count = Application.objects.filter(opportunity=opportunity).count()
    is_full = applicants_count >= opportunity.num_volunteers_needed
    is_closed = opportunity.is_filled or is_full

    return render(request, 'opportunities/opportunity_detail.html', {
        'opportunity': opportunity,
        'is_full': is_full,
    })

# Opportunity CRUD Views
class OpportunityUpdate(UpdateView):
    model = Opportunity
    form_class = OpportunityForm
    template_name = 'opportunities/opportunity_form.html'
    success_url = reverse_lazy('opportunity-list')

    def dispatch(self, request, *args, **kwargs):
        opportunity = self.get_object()
        if request.user != opportunity.organization.user and not request.user.is_superuser:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class OpportunityDelete(DeleteView):
    model = Opportunity
    template_name = 'opportunities/opportunity_confirm_delete.html'
    success_url = reverse_lazy('opportunity-list')

    def dispatch(self, request, *args, **kwargs):
        opportunity = self.get_object()
        if request.user != opportunity.organization.user and not request.user.is_superuser:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

# Mark Opportunity as Filled
@login_required
def mark_as_filled(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)

    if request.user != opportunity.organization.user:
        return redirect('home')

    opportunity.is_filled = True
    opportunity.save()

    return redirect('opportunity-detail', pk=opportunity.pk)

# Thank You After Applying
@login_required
def thank_you_for_applying(request, opportunity_id):
    opportunity = get_object_or_404(Opportunity, id=opportunity_id)
    return render(request, 'opportunities/thank_you_for_applying.html', {
        'opportunity': opportunity
    })

# List Applicants for Opportunity
@login_required
def applicants_list(request, id):
    opportunity = get_object_or_404(Opportunity, id=id)

    if request.user != opportunity.organization.user:
        return redirect('home')
    
    applications = Application.objects.filter(opportunity=opportunity).select_related('volunteer')

    return render(request, 'opportunities/applicants_list.html', {
        'opportunity': opportunity,
        'applications': applications
    })

# Email Application Confirmation
def send_application_email(volunteer, opportunity):
    subject = 'Application Confirmation'
    message = f'You have successfully applied for the opportunity "{opportunity.title}".'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [volunteer.user.email],
    )
