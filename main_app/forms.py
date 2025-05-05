# main_app/forms.py
from django import forms
from .models import Organization, VolunteerProfile, Application, Opportunity
import datetime

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'description', 'location', 'website']

class VolunteerProfileForm(forms.ModelForm):
    class Meta:
        model = VolunteerProfile
        fields = ['resume', 'qualifications', 'photo', 'interests']

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
            'is_active',
            'start_date',
            'end_date'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }
        
    organization = forms.ModelChoiceField(queryset=Organization.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and not user.is_superuser:
            del self.fields['organization']


    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < datetime.date.today():
            raise forms.ValidationError("Start date cannot be in the past.")
        return start_date

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')
        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError("End date must be after the start date.")
        return end_date