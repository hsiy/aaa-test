"""
This tests views relating to extra views associated with the report but not with sections
"""
from django.urls import reverse
from model_bakery import baker
from .test_basicViews import NonAACTest, ReportSetupTest

class ReportFirstPageTest(ReportSetupTest):
    """
    Test the first page of the report
    """
    def test_view(self):
        """
        Tests the response code and basic text labels expected
        """
        response = self.client.get(reverse('makeReports:rpt-first-page',kwargs={'pk':self.rpt.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response, "Author")
        self.assertContains(response, "Date")
        self.assertContains(response, "Form Entry")
    def test_view_DNE(self):
        """
        Tests the response code when the report does not exist returns 404
        """
        r = self.client.get(reverse('makeReports:rpt-first-page',kwargs={'pk':42}))
        self.assertEquals(r.status_code,404)
class FinalReportSupplementsTest(ReportSetupTest):
    """
    Tests the add final report supplements page
    """
    def setUp(self):
        super(FinalReportSupplementsTest,self).setUp()
        self.supp = baker.make('ReportSupplement')
    def test_view(self):
        """
        Tests response code and basic text expected
        """
        response = self.client.get(reverse('makeReports:rpt-sup-list',kwargs={'report':self.rpt.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response, "upplement")
        self.assertContains(response,self.supp.supplement.name)
class AddEndSupplementsTest(ReportSetupTest):
    """
    Test the add report supplement page
    """
    def test_view(self):
        """
        Tests response code and basic text expected
        """
        response = self.client.get(reverse('makeReports:add-rpt-sup',kwargs={'report':self.rpt.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"upplement")
class DeleteEndSupplementsTest(ReportSetupTest):
    """
    Tests deleting end supplements
    """
    def setUp(self):
        super(DeleteEndSupplementsTest,self).setUp()
        self.supp = baker.make('ReportSupplement')
    def test_view(self):
        """
        Tests response code and basic text expected
        """
        response = self.client.get(reverse('makeReports:delete-rpt-sup',kwargs={'report':self.rpt.pk,'pk':self.supp.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"elete")
        self.assertContains(response, "upplement")
        self.assertContains(response,self.supp.supplement.name)
class SubmitReportTest(ReportSetupTest):
    """
    Test submit report page
    """
    def test_view(self):
        """
        Tests response code and basic text expected
        """
        response = self.client.get(reverse('makeReports:submit-report',kwargs={'report':self.rpt.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,'SLO')
        self.assertContains(response,"Assessment")
        self.assertContains(response, "Data")
        self.assertContains(response,"Decision")
        self.assertContains(response,"Submit")
class SubmitSuccessTest(NonAACTest):
    """
    Tests submit success page
    """
    def test_view(self):
        response = self.client.get(reverse('makeReports:sub-suc'))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"submit")