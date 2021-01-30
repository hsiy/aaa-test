"""
This file contains tests to verify that all PDF views exist without error.
"""
from django.urls import reverse
from model_bakery import baker
from .test_basicViews import ReportAACSetupTest

class TestingPDFs(ReportAACSetupTest):
    """
    Class containing tests relating to the generation of PDFs
    """
    def test_GradedRubricPDF(self):
        """
        Tests the graded rubric PDf page exists
        """
        rub = baker.make("GradedRubric")
        baker.make("GradedRubricItem",rubric=rub)
        self.rpt.rubric = rub
        self.rpt.save()
        resp = self.client.get(reverse('makeReports:graded-rub-pdf',kwargs={
            'report': self.rpt.pk
        }))
        self.assertEquals(resp.status_code,200)
    def test_ReportPDFGen(self):
        """
        Tests that the report PDF without supplements page exists
        """
        resp = self.client.get(reverse('makeReports:report-pdf-no-sups',kwargs={
            'report':self.rpt.pk
        }))
        self.assertEquals(resp.status_code,200)
    def test_reportPDFwithSups(self):
        """
        Tests that the report PDF with supplements exists
        """
        resp = self.client.get(reverse('makeReports:report-pdf',kwargs={
            'report':self.rpt.pk
        }))
        self.assertEquals(resp.status_code,200)
    def test_ungradedRubricPDF(self):
        """
        Tests the the ungraded rubric generation page exists
        """
        rub = baker.make("Rubric")
        baker.make("RubricItem", rubricVersion=rub)
        resp = self.client.get(reverse('makeReports:rubric-auto-pdf',kwargs={
            'rubric':rub.pk
        }))
        self.assertEquals(resp.status_code,302)

