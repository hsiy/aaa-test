"""
Includes models principally managed by the AAC, which act both as Python objects and abstractions for database items
"""
from django.db import models
from django.utils.safestring import mark_safe
from makeReports.choices import LEVELS
from .basic_models import NonArchivedManager

class College(models.Model):
    """
    College model for colleges within the university
    """
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    
    objects = models.Manager()
    active_objects = NonArchivedManager()
    def __str__(self):
        return self.name
class Department(models.Model):
    """
    Department model for departments within colleges 
    """
    name = models.CharField(max_length=100)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    
    objects = models.Manager()
    active_objects = NonArchivedManager()    
    def __str__(self):
        return self.name
class DegreeProgram(models.Model):
    """
    Degree program model for degree programs within departments
    """
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=75, choices= LEVELS)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    cycle = models.IntegerField(blank=True, null=True)
    startingYear = models.PositiveIntegerField(blank=True, null=True, verbose_name="starting year of cycle")
    #not all degree programs are on a clear cycle
    active = models.BooleanField(default=True)
    accredited = models.BooleanField(default=False)
    objects = models.Manager()
    active_objects = NonArchivedManager()
    def __str__(self):
        return self.name
class Announcement(models.Model):
    """
    Model to hold annnoucements the AAC make
    """
    text = models.CharField(max_length=2000,blank=True)
    expiration = models.DateField()
    creation = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return mark_safe(self.text)
class RequiredFieldSetting(models.Model):
    """
    Model to hold settings for required field to submit report
    """
    name = models.CharField(max_length=200, blank=True, default="Setting")
    required = models.BooleanField(default=False)
