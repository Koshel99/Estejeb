# main_app/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Organization, Opportunity
from .forms import OrganizationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required


# Define the home view function
def home(request):
    organizations = Organization.objects.all()
    return render(request, 'home.html', {'organizations': organizations})

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
        if 'organization' in request.POST:
            organization_form = OrganizationForm(request.POST)
            user_form = UserCreationForm(request.POST)
            if organization_form.is_valid() and user_form.is_valid():
                # Create a new user
                user = user_form.save()
                # Assign the user to the organization
                organization = organization_form.save(commit=False)
                organization.user = user
                organization.save()
                login(request, user)
                return redirect('home')
        else:
            user_form = UserCreationForm(request.POST)
            if user_form.is_valid():
                user = user_form.save()
                login(request, user)
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