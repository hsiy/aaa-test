"""
This file contains models most directly related to assessments of SLOs, excluding data collection
"""
import os
from django.db import models
from makeReports.choices import FREQUENCY_CHOICES
from .basic_models import gd_storage

class Assessment(models.Model):
    """
    Assessment model collects assessments that are ostensibly the same except for minor changes,
    and includes fields which should never change
    """
    title = models.CharField(max_length=300)
    domainExamination = models.BooleanField(verbose_name="examination domain")
    domainProduct = models.BooleanField(verbose_name="product domain")
    domainPerformance = models.BooleanField(verbose_name="performance domain")
    directMeasure = models.BooleanField(verbose_name="direct measure")
    #false = indirect measure
    numberOfUses = models.PositiveIntegerField(default=0, verbose_name="number of uses")
    def __str__(self):
        return self.title

class AssessmentVersion(models.Model):
    """
    Specific versions of Assessments that occur within a report
    """
    report = models.ForeignKey('Report', on_delete=models.CASCADE)
    slo = models.ForeignKey('SLOInReport', on_delete=models.CASCADE, verbose_name="SLO in report")
    number = models.PositiveIntegerField(default=0)
    changedFromPrior = models.BooleanField(verbose_name="changed from prior version")
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=1000)
    finalTerm = models.BooleanField(verbose_name="final term")
    #false = final year
    where = models.CharField(max_length=500, verbose_name="location of assessment")
    allStudents = models.BooleanField(verbose_name="all students assessed")
    #false = sample of students
    sampleDescription = models.CharField(max_length=500,blank=True,null=True, verbose_name="description of sample")
    frequencyChoice = models.CharField(max_length=100,choices=FREQUENCY_CHOICES,default="O", verbose_name="frequency choice")
    frequency = models.CharField(max_length=500)
    #the below are percentage points
    threshold = models.CharField(max_length=500)
    target = models.PositiveIntegerField()
    supplements = models.ManyToManyField('AssessmentSupplement')
    def __str__(self):
        return self.assessment.title

class AssessmentSupplement(models.Model):
    """
    Supplemental files to assessments
    """
    supplement = models.FileField(
        upload_to='asssements/supplements', 
        storage=gd_storage, 
        validators=[])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return os.path.basename(self.supplement.name)
