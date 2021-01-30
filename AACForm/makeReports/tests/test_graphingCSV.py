"""
Tests graphing and CSV view pages exist
"""
from django.urls import reverse
from .test_basicViews import ReportAACSetupTest

class GraphPagesTests(ReportAACSetupTest):
    """
    Contains tests relating to the graphing pages
    """
    def test_aac_graphing(self):
        """
        Tests the AAC graphing pages exists
        """
        resp = self.client.get(reverse('makeReports:graphing'))
        self.assertEquals(resp.status_code,200)
    def test_dept_graphing(self):
        """
        Test the grpahing page for departments
        """
        resp = self.client.get(reverse('makeReports:graphing-dept',kwargs={
            'dept':self.rpt.degreeProgram.department.pk
        }))
        self.assertEquals(resp.status_code,200)
class CSVPagesTest(ReportAACSetupTest):
    """
    Contains tests relating to the CSV tests
    """
    def test_CSVByCollege(self):
        """
        Tests the CSV by college generator
        """
        resp = self.client.get(reverse('makeReports:csv-col',kwargs={
            'col':self.rpt.degreeProgram.department.college.pk,
            'gYear':2015,
            'lYear':2019
        }))
        self.assertEquals(resp.status_code,200)
    def test_CSVByDept(self):
        """
        Test the CSV by department page exists
        """
        resp = self.client.get(reverse('makeReports:csv-dept',kwargs={
            'dept':self.rpt.degreeProgram.department.pk,
            'gYear':2015,
            'lYear':2018
        }))
        self.assertEquals(resp.status_code,200)
    def test_CSVByDP(self):
        """
        Tests the CSV by degree program page exists
        """
        resp = self.client.get(reverse('makeReports:csv-dp',kwargs={
            'dept':self.rpt.degreeProgram.department.pk,
            'dP':self.rpt.degreeProgram.pk,
            'gYear':2014,
            'lYear':2014
        }))
        self.assertEquals(resp.status_code,200)
    def test_CSVManagement(self):
        """
        Ensures the CSV Management page exists
        """
        resp = self.client.get(reverse('makeReports:csv-mang'))
        self.assertEquals(resp.status_code,200)