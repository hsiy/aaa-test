"""
This file contains models most directly related to Student Learning Outcomes
"""
from django.db import models
from django.utils.safestring import mark_safe
from makeReports.choices import BLOOMS_CHOICES
from .basic_models import NonArchivedManager

class SLO(models.Model):
    """
    Model collects SLO in reports which are ostensibly  the same except minor changes, 
    includes only the attributes which should never change and counts how often it is used
    """
    blooms = models.CharField(choices=BLOOMS_CHOICES,max_length=50, verbose_name="Bloom's taxonomy level")
    gradGoals = models.ManyToManyField('GradGoal', verbose_name="graduate-level goals")
    numberOfUses = models.PositiveIntegerField(default=0, verbose_name="number of uses of this SLO")
class SLOInReport(models.Model):
    """
    A specific version of an SLO which occurs within a report
    """
    date = models.DateField()
    goalText = models.CharField(max_length=1000, verbose_name="goal text")
    slo = models.ForeignKey(SLO, on_delete=models.CASCADE, verbose_name="SLO")    
    changedFromPrior = models.BooleanField(verbose_name="changed from prior version")
    report = models.ForeignKey('Report', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(default=1)
    numberOfAssess = models.PositiveIntegerField(default=0, verbose_name="number of assessments")
    def __str__(self):
        return self.goalText

class GradGoal(models.Model):
    """
    A graduate goal graduate level programs may obtain
    """
    text = models.CharField(max_length=600)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = NonArchivedManager()
    def __str__(self):
        return mark_safe(self.text)
class SLOsToStakeholder(models.Model):
    """
    Text describing how SLOs are communicated to stakeholders
    """
    text = models.CharField(max_length=2000)
    report = models.ForeignKey('Report', on_delete=models.CASCADE, null=True)
    def __str__(self):
        return mark_safe(self.text)