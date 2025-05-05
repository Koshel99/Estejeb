# main_app/models.py

from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organizations')
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    website = models.URLField()


    def __str__(self):
        return self.name

class Opportunity(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    age_requirement = models.IntegerField()
    num_volunteers_needed = models.IntegerField()
    certification_required = models.BooleanField(default=False)
    certifications_list = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_filled = models.BooleanField(default=False)
    
    @property
    def is_filled(self):
        return getattr(self, '_is_filled', False)
    
    @is_filled.setter
    def is_filled(self, value):
        self._is_filled = value

    def __str__(self):
        return self.title

# We will explore
class Membership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('member', 'Member'), ('volunteer', 'Volunteer')])

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} - {self.role}"

# Volunteer based
class VolunteerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    qualifications = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    interests = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username

class Application(models.Model):
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_applications', default=1)  # default=1 refers to a User with ID=1
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='volunteer_applications', default=1)  # Similar here

    def __str__(self):
        return f"Application for {self.opportunity.title} by {self.user.username}"
