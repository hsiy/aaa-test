"""
This file contains models most directly related to grading and reviewing reports
"""
from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.safestring import mark_safe
from makeReports.choices import RUBRIC_GRADES_CHOICES, SECTIONS
from .basic_models import gd_storage

class Rubric(models.Model):
    """
    Model of rubric to collect rubric items and hold a file
    """
    date = models.DateField()
    fullFile = models.FileField(
        default='settings.STATIC_ROOT/norubric.pdf',
        verbose_name="rubric file",
        upload_to='rubrics', 
        storage=gd_storage, 
        null=True,
        blank=True, 
        validators=[FileExtensionValidator(allowed_extensions=('pdf',))])
    name = models.CharField(max_length = 150, default="Rubric")
    def __str__(self):
        return self.name
class GradedRubric(models.Model):
    """
    Model to collect graded rubric items and comments on a report
    """
    rubricVersion = models.ForeignKey(Rubric, on_delete=models.CASCADE, verbose_name="rubric version")
    section1Comment = models.CharField(max_length=2000,blank=True,null=True, verbose_name="section I comment")
    section2Comment = models.CharField(max_length=2000,blank=True,null=True, verbose_name="section II comment")
    section3Comment = models.CharField(max_length=2000,blank=True,null=True, verbose_name="section III comment")
    section4Comment = models.CharField(max_length=2000,blank=True,null=True, verbose_name="section IV comment")
    generalComment = models.CharField(max_length=2000,blank=True,null=True, verbose_name="general comment")
    complete = models.BooleanField(default=False)
    def __str__(self):
        return self.rubricVersion.name
class RubricItem(models.Model):
    """
    Model of individual items within a rubric
    """
    text = models.CharField(max_length=1000)
    section = models.PositiveIntegerField(choices=SECTIONS)
    rubricVersion = models.ForeignKey(Rubric, on_delete=models.CASCADE, verbose_name="rubric version")
    order = models.PositiveIntegerField(null=True, blank=True)
    abbreviation = models.CharField(max_length=20, default="", blank=True)
    DMEtext = models.CharField(max_length=1000, default="", blank=True, verbose_name="did not meet expectations text")
    MEtext = models.CharField(max_length=1000, default="", blank=True, verbose_name="met expectations text")
    EEtext = models.CharField(max_length=1000, default="", blank=True, verbose_name="exceeded expecations text")
    def __str__(self):
        return mark_safe(self.text)
class GradedRubricItem(models.Model):
    """
    Model individual items within a graded rubric
    """
    rubric = models.ForeignKey('GradedRubric', on_delete=models.CASCADE)
    item = models.ForeignKey(RubricItem, on_delete=models.CASCADE)
    grade = models.CharField(max_length=300, choices=RUBRIC_GRADES_CHOICES)
