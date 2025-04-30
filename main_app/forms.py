# main_app/forms.py
from django import forms
from .models import Organization, VolunteerProfile, Application, Opportunity

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'description', 'location', 'website']

class VolunteerProfileForm(forms.ModelForm):
    class Meta:
        model = VolunteerProfile
        fields = ['age', 'bio']

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = []
        
class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = [
            'title',
            'description',
            'location',
            'age_requirement',
            'num_volunteers_needed',
            'certification_required',
            'certifications_list',
            'is_active'
        ]