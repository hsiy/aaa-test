"""
This file contains models most directly related to data from assessments
"""
import os
from django.db import models
from makeReports.choices import SLO_STATUS_CHOICES
from .basic_models import gd_storage

class AssessmentData(models.Model):
    """
    Assessment data point for a particular assessment in a report
    """
    assessmentVersion = models.ForeignKey('AssessmentVersion',on_delete=models.CASCADE, verbose_name="assessment version")
    dataRange = models.CharField(max_length=500, verbose_name="data range")
    numberStudents = models.PositiveIntegerField(verbose_name="number of students")
    overallProficient = models.PositiveIntegerField(blank=True, verbose_name="overall percentage proficient")

class AssessmentAggregate(models.Model):
    """
    Aggregates the various assessments on different ranges for an aggregate success rate
    """ 
    assessmentVersion = models.OneToOneField('AssessmentVersion', on_delete=models.CASCADE, verbose_name="assessment version")
    aggregate_proficiency = models.PositiveIntegerField(verbose_name="aggregate proficiency percentage")
    met = models.BooleanField(verbose_name="target met")
    override = models.BooleanField(default=False)
    def __str__(self):
        return str(self.aggregate_proficiency)

class DataAdditionalInformation(models.Model):
    """
    Model to hold additional information about the data, possibly with a PDF supplement
    """
    report = models.ForeignKey('Report', on_delete=models.CASCADE)
    comment = models.CharField(max_length=3000, blank=True, default="")
    supplement = models.FileField(
        upload_to='data/supplements', 
        storage=gd_storage, 
        validators=[])
    def __str__(self):
        return os.path.basename(self.supplement.name)
class SLOStatus(models.Model):
    """
    Status of whether the target was met for an SLO
    """
    status = models.CharField(max_length=50, choices=SLO_STATUS_CHOICES)
    sloIR = models.OneToOneField('SLOInReport',on_delete=models.CASCADE)
    override = models.BooleanField(default=False)
class ResultCommunicate(models.Model):
    """
    Model holds the text for communicating results
    """
    text = models.CharField(max_length=3000)
    report = models.ForeignKey('Report', on_delete=models.CASCADE)
class Graph(models.Model):
    dateTime = models.DateTimeField()
    graph = models.FileField(
        upload_to='data/graphs', 
        storage=gd_storage,
    )