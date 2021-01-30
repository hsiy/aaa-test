"""
Includes most common models used extensively by all users across the site
"""
from django.db import models
from django.contrib.auth.models import User
from gdstorage.storage import GoogleDriveStorage

gd_storage = GoogleDriveStorage()
class NonArchivedManager(models.Manager):
    """
    Includes only active objects
    """
    def get_queryset(self):
        """
        Retrieves only active objects within type

        Returns:
            QuerySet : active objects only
        """
        return super().get_queryset().filter(active=True)
class Report(models.Model):
    """
    Report model which collects attributes specific to a report and completion status
    """
    year = models.PositiveIntegerField()
    author = models.CharField(max_length=100, blank=True)
    degreeProgram = models.ForeignKey('DegreeProgram', on_delete=models.CASCADE, verbose_name="degree program")
    accredited = models.BooleanField(default=False)
    date_range_of_reported_data = models.CharField(max_length=500,blank=True, null=True)
    rubric = models.OneToOneField('GradedRubric', on_delete=models.SET_NULL, null=True)
    section1Comment = models.CharField(max_length=2000, blank=True, null=True, verbose_name="section I comment")
    section2Comment = models.CharField(max_length=2000, blank=True, null=True, verbose_name="section II comment")
    section3Comment = models.CharField(max_length=2000, blank=True, null=True, verbose_name="section III comment")
    section4Comment = models.CharField(max_length=2000, blank=True, null=True, verbose_name="section IV comment")
    submitted = models.BooleanField()
    returned = models.BooleanField(default=False)
    numberOfSLOs = models.PositiveIntegerField(default=0, verbose_name="number of SLOs")
class Profile(models.Model):
    """
    Model to hold extra information in addition to Django's User class, including whether they are 
    AAC members and the department
    """
    #first name, last name and email are included in the built-in User class. Access them through the user field
    aac = models.BooleanField(null=True)
    #False = faculty member/dept account
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
