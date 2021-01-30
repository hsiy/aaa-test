"""
This file contains tests relating to SLO views
"""
from django.urls import reverse
from makeReports.models import SLOInReport
from makeReports.choices import BLOOMS_CHOICES
from model_bakery import baker
from .test_basicViews import ReportSetupTest


class SLOSummaryGRTest(ReportSetupTest):
    """
    Tests the SLO summary page for graduate programs
    """
    def setUp(self):
        """
        Setups an SLO in the current report
        """
        super(SLOSummaryGRTest,self).setUp()
        self.rpt.degreeProgram.level = "GR"
        self.rpt.degreeProgram.save()
        self.slo = baker.make('SLOInReport', make_m2m=True, report=self.rpt)
        self.slo2 = baker.make('SLOInReport',make_m2m=True, report=self.rpt)
    def test_view(self):
        """
        Tests response code and existence of SLO
        """
        response = self.client.get(reverse('makeReports:slo-summary',kwargs={'report':self.rpt.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"SLO")
        self.assertContains(response, self.slo.goalText)
        self.assertContains(response, self.slo2.goalText)
        for gg in self.slo.slo.gradGoals.all():
            self.assertContains(response, gg.text)
        for gg in self.slo2.slo.gradGoals.all():
            self.assertContains(response, gg.text)
class SLOSummaryGRTestRecipes(SLOSummaryGRTest):
    """
    Tests summary for graduate programs using recipes instead of random
    """
    def setUp(self):
        """
        Set-ups SLOs using the recipes
        """
        super().setUp()
        self.slo = baker.make_recipe('makeReports.sloInReport',report=self.rpt)
        self.slo2 = baker.make_recipe('makeReports.sloInReport',report=self.rpt)
class SLOSummaryUGTest(ReportSetupTest):
    """
    Tests SLO summary page for undergraduate programs
    """
    def setUp(self):
        """
        Setups an SLO in the current report
        """
        super(SLOSummaryUGTest,self).setUp()
        self.rpt.degreeProgram.level = "UG"
        self.rpt.degreeProgram.save()
        self.slo = baker.make('SLOInReport', make_m2m=False, report=self.rpt)
        self.slo2 = baker.make('SLOInReport',make_m2m=False, report=self.rpt)
    def test_view(self):
        """
        Tests response code and existence of SLO
        """
        response = self.client.get(reverse('makeReports:slo-summary',kwargs={'report':self.rpt.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"SLO")
        self.assertContains(response, self.slo.goalText)
        self.assertContains(response, self.slo2.goalText)
        self.assertNotContains(response,"Grad")
class SLOSummaryUGTestRecipe(SLOSummaryUGTest):
    """
    Tests SLO summary for UG programs using recipes
    """
    def setUp(self):
        """
        Sets up SLOs using recipes
        """
        super().setUp()
        self.slo = baker.make_recipe('makeReports.sloInReport', report=self.rpt)
        self.slo2 = baker.make_recipe('makeReports.sloInReport', report=self.rpt)
class AddSLOGRTestPage(ReportSetupTest):
    """
    Tests add SLO page exists for graduate programs
    """
    def setUp(self):
        """
        Sets level of program of report
        """
        super(AddSLOGRTestPage,self).setUp()
        self.rpt.degreeProgram.level="GR"
        self.rpt.degreeProgram.save()
    def test_view(self):
        """
        Tests response and basic expected text
        """
        response = self.client.get(reverse('makeReports:add-slo',kwargs={'report':self.rpt.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"SLO")
        self.assertContains(response,"Bloom")
        self.assertContains(response,"Graduate")
    def test_post(self):
        """
        Tests post creates SLO
        """
        form_data = {
            'text':'The students can write reports with solid mechanics.',
            'blooms': BLOOMS_CHOICES[1][0]
        }
        self.client.post(reverse('makeReports:add-slo',kwargs={'report':self.rpt.pk}),form_data)
        s = SLOInReport.objects.filter(goalText='The students can write reports with solid mechanics.').count()
        self.assertTrue(s)
    def test_post_bloom_fail(self):
        """
        Tests that posting invalid Bloom option fails
        """
        form_data = {
            'text':'The students can write reports with biological terms.',
            'blooms': "not a blooms choice"
        }
        self.client.post(reverse('makeReports:add-slo',kwargs={'report':self.rpt.pk}),form_data)
        s = SLOInReport.objects.filter(goalText='The students can write reports with biological terms.').count()
        self.assertFalse(s>0)
    def test_post_too_long_fail(self):
        """
        Tests that posting too long of text fails
        """
        reallyLong = "Students will use a microscope."*501
        form_data = {
            'text':reallyLong,
            'blooms': BLOOMS_CHOICES[1][0]
        }
        self.client.post(reverse('makeReports:add-slo',kwargs={'report':self.rpt.pk}),form_data)
        s = SLOInReport.objects.filter(goalText=reallyLong).count()
        self.assertFalse(s>0)
class AddSLOUGTestPage(ReportSetupTest):
    """
    Test add SLO page exists for undergraduate programs
    """
    def setUp(self):
        """
        Sets level of program of report
        """
        super(AddSLOUGTestPage,self).setUp()
        self.rpt.degreeProgram.level ="UG"
        self.rpt.degreeProgram.save()
    def test_view(self):
        """
        Tests response and basic expected text
        """
        response = self.client.get(reverse('makeReports:add-slo',kwargs={'report':self.rpt.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"SLO")
        self.assertContains(response,"Bloom")
        self.assertNotContains(response,"Graduate")
    def test_post(self):
        """
        Tests post creates SLO
        """
        form_data = {
            'text':'Students will design physics experiments.',
            'blooms': BLOOMS_CHOICES[1][0]
        }
        self.client.post(reverse('makeReports:add-slo',kwargs={'report':self.rpt.pk}),form_data)
        s = SLOInReport.objects.filter(goalText='Students will design physics experiments.').count()
        self.assertTrue(s)
    def test_post_too_long_fail(self):
        """
        Tests that posting too long of text fails
        """
        reallyLong = "Students will write reports."*501
        form_data = {
            'text':reallyLong,
            'blooms': BLOOMS_CHOICES[1][0]
        }
        self.client.post(reverse('makeReports:add-slo',kwargs={'report':self.rpt.pk}),form_data)
        s = SLOInReport.objects.filter(goalText=reallyLong).count()
        self.assertFalse(s>0)
class ImportSLOTestPage(ReportSetupTest):
    """
    Test import SLO page exists
    """
    def setUp(self):
        """
        Creates SLO within and out of the department
        """
        super(ImportSLOTestPage,self).setUp()
        self.inDp = baker.make('DegreeProgram',department=self.dept)
        self.oRpt = baker.make("Report",degreeProgram=self.inDp, year=self.rpt.year)
        self.inSLO = baker.make("SLOInReport",report=self.oRpt)
        self.outSLO = baker.make("SLOInReport", report__year=self.rpt.year)
    def test_view(self):
        """
        Tests response and that expected SLO shows up from search
        """
        response = self.client.get(reverse('makeReports:import-slo',kwargs={"report":self.rpt.pk})+"?dp="+str(self.inDp.pk)+"&year="+str(self.rpt.year))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"SLO")
        self.assertContains(response,self.inSLO.goalText)
        self.assertNotContains(response,self.outSLO.goalText)
    def test_post(self):
        """
        Tests that the import posts
        """
        num = self.rpt.numberOfSLOs
        fD = {
            'slo': self.inSLO.pk
        }
        self.client.post(reverse('makeReports:import-slo',kwargs={"report":self.rpt.pk})+"?dp="+str(self.inDp.pk)+"&year="+str(self.rpt.year),fD)
        self.rpt.refresh_from_db()
        self.assertEquals(num+1,self.rpt.numberOfSLOs)
        self.assertEquals(1,SLOInReport.objects.filter(report=self.rpt).count())
class ImportSLOTestRecipe(ImportSLOTestPage):
    """
    Tests importing SLOs using recipe created SLOs
    """
    def setUp(self):
        """
        Sets up the SLOs in and out of department
        """
        super().setUp()
        self.inDp = baker.make_recipe('makeReports.degreeProgram',department=self.dept)
        self.oRpt = baker.make_recipe('makeReports.report', degreeProgram=self.inDp, year=self.rpt.year)
        self.inSLO = baker.make_recipe('makeReports.sloInReport',report=self.oRpt)
        self.outSLO = baker.make_recipe('makeReports.sloInReport', report__year=self.rpt.year)
class EditNewSLOPageTest(ReportSetupTest):
    """
    Tests edit new SLO page
    """
    def setUp(self):
        """
        Creates new SLO
        """
        super(EditNewSLOPageTest,self).setUp()
        self.slo = baker.make("SLOInReport",slo__numberOfUses=1)
        self.slo.slo.numberOfUses = 1
        self.slo.slo.save()
    def test_view(self):
        """
        Tests response and basic expected text
        """
        response = self.client.get(reverse('makeReports:edit-new-slo',kwargs={'report':self.rpt.pk,'sloIR':self.slo.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"SLO")
        self.assertContains(response,"Bloom")
class EditNewSLOPageTestRecipe(EditNewSLOPageTest):
    """
    Tests editing new SLO using fixtures made with recipes
    """
    def setUp(self):
        """
        Sets up the SLO
        """
        super().setUp()
        self.slo = baker.make_recipe('makeReports.sloInReport',slo__numberOfUses=1)
        self.slo.slo.numberOfUses = 1
        self.slo.slo.save()
class EditImptedSLOPageTest(ReportSetupTest):
    """
    Tests edit imported SLO page
    """
    def setUp(self):
        """
        Creates new SLO
        """
        super(EditImptedSLOPageTest,self).setUp()
        self.slo = baker.make("SLOInReport",slo__numberOfUses=3)
    def test_view(self):
        """
        Tests response and basic expected text
        """
        response = self.client.get(reverse('makeReports:edit-impt-slo',kwargs={'report':self.rpt.pk,'sloIR':self.slo.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"SLO")
        self.assertNotContains(response,"Bloom")
        self.assertNotContains(response,"Graduate Goal")
class EditImptedSLOPageTestRecipe(EditImptedSLOPageTest):
    """
    Tests the editing of imported SLOs with recipe made fixtures
    """
    def setUp(self):
        """
        Creates the SLO from a recipe
        """
        super().setUp()
        self.slo = baker.make_recipe('makeReports.sloInReport',slo__numberOfUses=3)
class SLOStakeholderTest(ReportSetupTest):
    """
    Tests SLO stakeholder page
    """
    def test_view(self):
        """
        Tests response and basic expected text
        """
        response = self.client.get(reverse('makeReports:slo-stakeholders',kwargs={"report":self.rpt.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"Stakeholder")
class SLOStakeImportTest(ReportSetupTest):
    """
    Tests SLO stakeholder communication import page
    """
    def setUp(self):
        """
        Create stakeholder to check importing
        """
        super(SLOStakeImportTest,self).setUp()
        self.dPI = baker.make('DegreeProgram',department=self.dept)
        self.stkToImpt = baker.make('SLOsToStakeholder',report__degreeProgram=self.dPI, report__year=self.rpt.year)
        self.stkNotImpt = baker.make("SLOsToStakeholder",report__degreeProgram=self.dPI,report__year=self.rpt.year-1)
        dept2 = baker.make("Department")
        self.stkNotImpt2 = baker.make("SLOsToStakeholder",report__degreeProgram__department=dept2,report__year=self.rpt.year)
    def test_view(self):
        """
        Tests response code and that the stakeholder to import was found
        """
        response = self.client.get(str(reverse('makeReports:slo-stk-import',kwargs={"report":self.rpt.pk}))+"?dp="+str(self.dPI.pk)+"&year="+str(self.rpt.year))
        self.assertEquals(response.status_code,200)
        self.assertContains(response, "takeholder")
        self.assertContains(response, self.stkToImpt.text)
        self.assertNotContains(response, self.stkNotImpt.text)
        self.assertNotContains(response, self.stkNotImpt2.text) 
class SLOStakeImportTestRecipe(SLOStakeImportTest):
    """
    Tests the SLO stakeholder page using recipes
    """
    def setUp(self):
        """
        Creates stakeholder to check while importing using recipes
        """
        super().setUp()
        self.dPI = baker.make_recipe('makeReports.degreeProgram',department=self.dept)
        self.stkToImpt = baker.make_recipe('makeReports.slosToStakeholder',report__degreeProgram=self.dPI,report__year=self.rpt.year)
        self.stkNotImpt = baker.make_recipe('makeReports.slosToStakeholder',report__degreeProgram=self.dPI,report__year=self.rpt.year-1)
        dept2 = baker.make_recipe('makeReports.department')
        self.stkNotImpt2 = baker.make_recipe('makeReports.slosToStakeholder',report__degreeProgram__department=dept2,report__year=self.rpt.year)   
class SLOCommentTest(ReportSetupTest):
    """
    Test SLO section comment page
    """
    def test_view(self):
        """
        Tests response code
        """
        response = self.client.get(reverse('makeReports:slo-comment',kwargs={"report":self.rpt.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"omment")
class DeleteNewSLOPageTest(ReportSetupTest):
    """
    Tests the delete SLO page
    """
    def setUp(self):
        """
        Creates an SLO to delete
        """
        super(DeleteNewSLOPageTest,self).setUp()
        self.sSLO = baker.make("SLO",numberOfUses=1)
        self.slo = baker.make("SLOInReport",report=self.rpt, slo=self.sSLO)
        self.sSLO.numberOfUses=1
        self.sSLO.save()
    def test_view(self):
        """
        Checks the page exists
        """
        response = self.client.get(reverse('makeReports:delete-new-slo',kwargs={'report':self.rpt.pk,'pk':self.slo.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"SLO")
class DeleteImportedSLOPageTest(ReportSetupTest):
    """
    Tests the delete imported SLO page
    """
    def setUp(self):
        """
        Creates pyan SLO to delete
        """
        super(DeleteImportedSLOPageTest,self).setUp()
        self.rpt.numberOfSLOs = 3
        self.rpt.save()
        self.sSLO = baker.make("SLO",numberOfUses=3)
        self.slo = baker.make("SLOInReport",report=self.rpt, slo=self.sSLO)
    def test_view(self):
        """
        Checks page exists
        """
        response = self.client.get(reverse('makeReports:delete-impt-slo',kwargs={'report':self.rpt.pk,'pk':self.slo.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"SLO")
    def test_view_DNE(self):
        """
        Tests the response code from the Delete Imported SLO page when the item does not exist returns 404
        """
        r = self.client.get(reverse('makeReports:delete-impt-slo',kwargs={'report':self.rpt.pk,'pk':423}))
        self.assertEquals(r.status_code,404)
    def test_post(self):
        """
        Tests delete posts
        """
        pk = self.slo.pk
        self.client.post(reverse('makeReports:delete-impt-slo',kwargs={'report':self.rpt.pk,'pk':pk}),follow=True)
        self.assertRaises(SLOInReport.DoesNotExist, SLOInReport.objects.get,pk=pk)
