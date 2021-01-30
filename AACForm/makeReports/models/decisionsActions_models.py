"""
This file contains models most directly related to decisions and actions
"""
import os
from django.db import models
from .basic_models import gd_storage

class DecisionsActions(models.Model):
    """
    Model of decisions/actions for a report
    """
    sloIR = models.OneToOneField('SLOInReport', on_delete=models.CASCADE)
    text = models.CharField(max_length=3000, blank=True, default="")

class ReportSupplement(models.Model):
    """
    Model to hold supplements to the report as a whole
    """
    supplement = models.FileField(
        upload_to='data/supplements', 
        storage=gd_storage,
        validators=[])
    report = models.ForeignKey('Report', on_delete=models.CASCADE)
    def __str__(self):
        return os.path.basename(self.supplement.name)