"""
This tests the SLO forms work as expected
"""
from django.test import TestCase
from makeReports.models import SLOInReport, SLOsToStakeholder
from model_bakery import baker
from makeReports.forms import CreateNewSLO, ImportSLOForm, ImportStakeholderForm
from makeReports.choices import BLOOMS_CHOICES

class SLOFormsTest(TestCase):
    """
    Tests forms related to SLOs
    """
    def test_create_valid(self):
        """
        Tests that CreateNewSLO properly accepts valid data
        """
        gg = baker.make("GradGoal")
        f = CreateNewSLO({
            'text':'Students will acknowlege the affect of the criminal justice system.',
            'blooms':BLOOMS_CHOICES[1][0],
            'gradGoals':gg.pk
        })
        self.assertTrue(f.is_valid())
    def test_import_valid(self):
        """
        Tests that ImportSLOForm accepts valid data
        """
        slo = baker.make("SLOInReport")
        f = ImportSLOForm({
            'slo':[slo.pk],
            'importAssessments': False
        },sloChoices=SLOInReport.objects.all())
        self.assertTrue(f.is_valid())
    def test_import_invalid(self):
        """
        Tests that ImportSLOForm rejects non SLOs
        """
        f = ImportSLOForm({
            'slo':'Students will analyze text carefully by using several outside sources.',
            'importAssessments': False
        },sloChoices=SLOInReport.objects.all())
        self.assertFalse(f.is_valid())
    def test_impt_stk_valid(self):
        """
        Tests that ImportStakeholderForm accepts valid data
        """
        stk = baker.make("SLOsToStakeholder")
        f = ImportStakeholderForm({
            'stk':stk.pk
        },stkChoices=SLOsToStakeholder.objects.all())
        self.assertTrue(f.is_valid())