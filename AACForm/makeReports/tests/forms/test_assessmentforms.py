"""
This tests the assessment forms work as expected
"""
from django.test import TestCase
from makeReports.models import AssessmentVersion, SLOInReport
from model_bakery import baker
from makeReports.forms import CreateNewAssessment, ImportAssessmentForm
from makeReports.choices import FREQUENCY_CHOICES

class AssessmentFormTests(TestCase):
    """
    Tests that assessment forms work as expected
    """
    def test_create_new_valid(self):
        """
        Tests that CreateNewAssessment properly accepts valid data
        """
        slo = baker.make("SLOInReport")
        f = CreateNewAssessment({
            'slo':slo.pk,
            'title':'Final Report',
            'description':'Students will write a report describing their capstone project.',
            'domain':["Pe"],
            'directMeasure':True,
            'finalTerm':False,
            'where':'kldsfj',
            'allStudents':True,
            'sampleDescription':'',
            'frequencyChoice': FREQUENCY_CHOICES[0][0],
            'frequency':'',
            'threshold':'Students must be rated proficient.',
            'target':93
        },sloQS=SLOInReport.objects.all())
        self.assertTrue(f.is_valid())
        
    def test_create_new_invalid(self):
        """
        Tests that CreateNewAssessment reject when not all fields are present
        """
        slo = baker.make("SLOInReport")
        f = CreateNewAssessment({
            'slo':slo.pk,
            'domain':["Pe"],
            'directMeasure':True,
            'finalTerm':False,
            'where':'During ENGL 5090',
            'allStudents':True,
            'sampleDescription':'All students',
            'frequencyChoice': FREQUENCY_CHOICES[0][0],
            'frequency':'Every semester',
            'target':93
        },sloQS=SLOInReport.objects.all()
        )
        self.assertFalse(f.is_valid())
    def test_import_form(self):
        """
        Tests the ImportAssessmentForm takes valid data
        """
        a = baker.make("AssessmentVersion")
        s = baker.make("SLOInReport")
        f = ImportAssessmentForm({
            'assessment':[a.pk],
            'slo':s.pk
        },assessChoices=AssessmentVersion.objects.all(),
            slos=SLOInReport.objects.all()
        )
        print(f.errors)
        self.assertTrue(f.is_valid())
    def test_import_form_invalid(self):
        """
        Tests the ImportAssessmentForm rejects when assessment is not in the QuerySet
        """
        a = baker.make("AssessmentVersion")
        baker.make("AssessmentVersion")
        s = baker.make("SLOInReport")
        f = ImportAssessmentForm({
            'assessment':[a.pk],
            'slo':s.pk
        },assessChoices=AssessmentVersion.objects.all().exclude(pk=a.pk),
            slos=SLOInReport.objects.all()
        )
        self.assertFalse(f.is_valid())
    
