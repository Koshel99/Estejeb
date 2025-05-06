# main_app/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Organization, Opportunity, VolunteerProfile, Application
from .forms import OrganizationForm, VolunteerProfileForm, OpportunityForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings

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

# Define the signup view function
def signup(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        organization_form = OrganizationForm(request.POST)
        volunteer_form = VolunteerProfileForm(request.POST)

        if user_form.is_valid():
            user = user_form.save(commit=False)  # Don't save yet so we can attach the right profile
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
        # else: one or more forms were invalid
    else:
        user_form = UserCreationForm()
        organization_form = OrganizationForm()
        volunteer_form = VolunteerProfileForm()

    return render(request, 'signup.html', {
        'user_form': user_form,
        'organization_form': organization_form,
        'volunteer_form': volunteer_form
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

            return redirect('organization-profile', id=organization.id)
        else:
            print(form.errors)
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
    
@login_required
def organization_details(request, id):
    organization = get_object_or_404(Organization, id=id)
    is_owner_or_superuser = (organization.user == request.user or request.user.is_superuser)
    
    opportunities = organization.opportunity_set.all()
    
    return render(
        request,
        'organizations/organization_details.html',
        {
            'organization': organization,
            'is_owner_or_superuser': is_owner_or_superuser,
            'opportunities': opportunities,
        }
    )
# Volunteer:

@login_required
def volunteer_profile(request, id):
    volunteer_profile = get_object_or_404(VolunteerProfile, id=id)

    return render(request, 'volunteers/volunteer_profile.html', {
        'volunteer_profile': volunteer_profile
    })

def view_all_volunteers(request):
    # Fetch all volunteer profiles
    volunteers = VolunteerProfile.objects.all()
    return render(request, 'volunteers/view_all_volunteers.html', {'volunteers': volunteers})

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
            return redirect('volunteer-profile', id=volunteer_profile.id)
    else:
        form = VolunteerProfileForm(instance=volunteer_profile)

    return render(request, 'volunteers/volunteer_edit.html', {
        'form': form,
        'volunteer_profile': volunteer_profile
    })

@login_required
@require_POST
def volunteer_delete(request, id):
    volunteer_profile = get_object_or_404(VolunteerProfile, id=id)

    if request.user != volunteer_profile.user:
        return redirect('home')

    volunteer_profile.delete()
    return redirect('signup')

# Opportunity
@login_required
def apply_to_opportunity(request, id):

    opportunity = get_object_or_404(Opportunity, id=id)

    volunteer_profile = VolunteerProfile.objects.filter(user=request.user).first()
    
    if not volunteer_profile:
        return redirect('create_volunteer_profile')

    if Application.objects.filter(volunteer=volunteer_profile, opportunity=opportunity).exists():
        return render(request, 'opportunities/already_applied.html')

    Application.objects.create(volunteer=volunteer_profile, opportunity=opportunity)

    return redirect('thank_you_for_applying') 

def opportunity_list(request):
    opportunities = Opportunity.objects.all()
    return render(request, 'opportunities/opportunity_list.html', {'opportunities': opportunities})

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
            print(form.errors)
    else:
        form = OpportunityForm(user=request.user)

    return render(request, 'opportunities/create_opportunity.html', {'form': form})

def opportunity_detail(request, id):
    opportunity = get_object_or_404(Opportunity, id=id)

    applicants_count = Application.objects.filter(opportunity=opportunity).count()

    is_full = applicants_count >= opportunity.num_volunteers_needed
    is_closed = opportunity.is_filled or is_full

    return render(request, 'opportunities/opportunity_detail.html', {
        'opportunity': opportunity,
        'is_full': is_full,
    })
    
def opportunity_update(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)

    if request.user == opportunity.organization.user or request.user.is_superuser:
        if request.method == 'POST':
            form = OpportunityForm(request.POST, instance=opportunity)
            if form.is_valid():
                form.save()
                return redirect('opportunity-detail', pk=opportunity.pk)
        else:
            form = OpportunityForm(instance=opportunity)

        return render(request, 'opportunities/opportunity_update.html', {'form': form})

    return redirect('home')


def opportunity_delete(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)

    if request.user == opportunity.organization.user or request.user.is_superuser:
        opportunity.delete()
        return redirect('home')

    return redirect('home')

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
    
@login_required
def apply_to_opportunity(request, id):
    opportunity = get_object_or_404(Opportunity, id=id)

    volunteer_profile = VolunteerProfile.objects.filter(user=request.user).first()

    if not volunteer_profile:
        return redirect('create_volunteer_profile')

    if Application.objects.filter(volunteer=volunteer_profile, opportunity=opportunity).exists():
        return render(request, 'opportunities/already_applied.html')

    Application.objects.create(volunteer=volunteer_profile, opportunity=opportunity)

    return redirect('thank-you-for-applying', opportunity_id=id)

@login_required
def mark_as_filled(request, id):
    opportunity = get_object_or_404(Opportunity, id=id)
    
    if request.user != opportunity.organization.user:
        return redirect('home')
    
    opportunity.is_filled = True
    opportunity.save()

    return redirect('opportunity-detail', id=opportunity.id)

@login_required
def thank_you_for_applying(request, opportunity_id):
    opportunity = get_object_or_404(Opportunity, id=opportunity_id)
    return render(request, 'opportunities/thank_you_for_applying.html', {
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
    

# Other

def send_application_email(volunteer, opportunity):
    subject = 'Application Confirmation'
    message = f'You have successfully applied for the opportunity "{opportunity.title}".'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [volunteer.user.email],
        fail_silently=False,
    )