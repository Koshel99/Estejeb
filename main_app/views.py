# main_app/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Organization, Opportunity, VolunteerProfile, Application
from .forms import OrganizationForm, VolunteerProfileForm, OpportunityForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required


# Define the home view function
def home(request):
    organizations = Organization.objects.all().order_by('-id')[:4]
    opportunities = Opportunity.objects.all().order_by('-id')[:4]
    return render(request, 'home.html', {
        'organizations': organizations,
        'opportunities': opportunities
    })

# Define the about view function
def about(request):
    return render(request, 'about.html')

# admin
def profile(request):
    return  render(request, 'home.html')

# Define the admin function
def signup(request):
    error_message = ''
    
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        organization_form = OrganizationForm(request.POST)

        if user_form.is_valid():
            user = user_form.save()
            login(request, user)

            # Check if they signed up as an organization
            if 'organization' in request.POST:
                if organization_form.is_valid():
                    organization = organization_form.save(commit=False)
                    organization.user = user
                    organization.save()
                else:
                    error_message = 'Organization form invalid.'
            else:
                # Create a VolunteerProfile
                VolunteerProfile.objects.create(user=user, age=0, bio="")  # Default placeholder values

            return redirect('home')
        else:
            error_message = 'Invalid sign up - try again'
    
    else:
        user_form = UserCreationForm()
        organization_form = OrganizationForm()

    return render(request, 'signup.html', {
        'user_form': user_form,
        'organization_form': organization_form,
        'error_message': error_message
    })


# Define the organization function
@login_required
def organization_profile(request, id):
    company_profile = get_object_or_404(Organization, id=id)
    opportunities = Opportunity.objects.filter(organization=company_profile, is_active=True)
    return render(request, 'organizations/organization_profile.html', {
        'company_profile': company_profile,
        'opportunities': opportunities
    })

def organization_list(request):
    organizations = Organization.objects.all()  # Fetch all organizations
    return render(request, 'organizations/organization_list.html', {'organizations': organizations})

@login_required
def create_organization(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save(commit=False)
            organization.user = request.user
            organization.save()
            return redirect('organization-detail', pk=organization.pk)
    else:
        form = OrganizationForm()
        
        
    return render(request, 'organizations/organization_form.html', {'form': form})

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
    
# Volunteer:

@login_required
def create_volunteer_profile(request):
    if request.method == 'POST':
        form = VolunteerProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('home')
    else:
        form = VolunteerProfileForm()
    return render(request, 'volunteers/volunteer_profile_form.html', {'form': form})

@login_required
def volunteer_profile(request):
    # Fetch the volunteer profile based on the logged-in user
    volunteer_profile = get_object_or_404(VolunteerProfile, user=request.user)

    return render(request, 'volunteers/volunteer_profile.html', {
        'volunteer_profile': volunteer_profile
})

# Opportunity
@login_required
def apply_to_opportunity(request, id):
    opportunity = get_object_or_404(Opportunity, id=id)
    volunteer_profile = get_object_or_404(VolunteerProfile, user=request.user)

    if Application.objects.filter(volunteer=volunteer_profile, opportunity=opportunity).exists():
        return render(request, 'opportunities/already_applied.html')

    Application.objects.create(volunteer=volunteer_profile, opportunity=opportunity)
    return redirect('home')

def opportunity_list(request):
    opportunities = Opportunity.objects.all()
    return render(request, 'opportunities/opportunity_list.html', {'opportunities': opportunities})

@login_required
def create_opportunity(request):
    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.save(commit=False)
            opportunity.organization = request.user.organization  # assuming `organization` is linked to user
            opportunity.save()
            return redirect('opportunity-list')
    else:
        form = OpportunityForm()

    return render(request, 'opportunities/create_opportunity.html', {'form': form})

def opportunity_detail(request, id):
    opportunity = get_object_or_404(Opportunity, id=id)
    return render(request, 'opportunities/opportunity_detail.html', {
        'opportunity': opportunity
    })
    
class OpportunityUpdate(UpdateView):
    model = Opportunity
    form_class = OpportunityForm
    template_name = 'opportunities/opportunity_form.html'
    success_url = reverse_lazy('opportunity-list')

class OpportunityDelete(DeleteView):
    model = Opportunity
    template_name = 'opportunities/opportunity_confirm_delete.html'
    success_url = reverse_lazy('opportunity-list')

# Application
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