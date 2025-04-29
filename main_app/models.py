# main_app/models.py

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class Organization(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    website = models.URLField()

    def __str__(self):
        return self.name

class Opportunity(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    age_requirement = models.PositiveIntegerField()
    num_volunteers_needed = models.PositiveIntegerField()
    certification_required = models.BooleanField(default=False)
    certifications_list = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

# We will explore
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('member', 'Member'), ('volunteer', 'Volunteer')])

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} - {self.role}"
