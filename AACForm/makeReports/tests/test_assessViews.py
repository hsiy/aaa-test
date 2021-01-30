"""
Tests relating to the Assessment Views
"""
from django.urls import reverse
from makeReports.models import Assessment, AssessmentVersion, AssessmentSupplement
from makeReports.choices import FREQUENCY_CHOICES
from model_bakery import baker
from .test_basicViews import ReportSetupTest, getWithReport, postWithReport

class AssessmentSummaryPageTest(ReportSetupTest):
    """
    Tests Assessment summary page and comment page
    """
    def setUp(self):
        """
        Sets up assessments to be on the page
        """
        super(AssessmentSummaryPageTest,self).setUp()
        self.assess = baker.make("AssessmentVersion",report=self.rpt)
        self.assess2 = baker.make("AssessmentVersion",report=self.rpt)
        self.assessNotInRpt = baker.make("AssessmentVersion")
    def test_view(self):
        """
        Test view exists with assessments on it
        """
        response = self.client.get(reverse('makeReports:assessment-summary',kwargs={'report':self.rpt.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,self.assess.assessment.title)
        self.assertContains(response,self.assess2.assessment.title)
        self.assertNotContains(response, self.assessNotInRpt.assessment.title)
    def test_comment_page(self):
        response = getWithReport('assessment-comment',self,{},"")
        self.assertEquals(response.status_code,200)
class AssessmentSummaryPageTestRecipe(AssessmentSummaryPageTest):
    """
    Tests Assessment summary page and comment page using recipes instead of random
    """
    def setUp(self):
        """
        Sets up the assessments from recipes to be used on the page
        """
        super().setUp()
        self.assess = baker.make_recipe("makeReports.assessmentVersion",report=self.rpt)
        self.assess2 = baker.make_recipe("makeReports.assessmentVersion",report=self.rpt)
        r2 = baker.make("Report")
        self.assessNotInRpt = baker.make_recipe("makeReports.assessmentVersion",report=r2)
class AddNewAssessmentTest(ReportSetupTest):
    """
    Tests the Add New Assessment Page
    """
    def test_view(self):
        """
        Tests view exists
        """
        response = self.client.get(reverse('makeReports:add-assessment',kwargs={'report':self.rpt.pk}))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"ssessment")
    def test_post(self):
        """
        Tests that the assessment is added
        """
        slo = baker.make("SLOInReport", report=self.rpt)
        fD = {
            'slo': slo.pk,
            'title': 'Final performance',
            'description': 'Students will write an original play and use fellow students are actors.',
            'domain': ["Pe","Pr"],
            'directMeasure':True,
            'finalTerm':True,
            'where': 'The final semester by appointment',
            'allStudents': True,
            'sampleDescription':'Students who are graduating',
            'frequencyChoice': FREQUENCY_CHOICES[0][0],
            'frequency':'Only during the summer semester.',
            'threshold':'Recieves at least 85 on the rubric',
            'target':34
        }
        self.client.post(reverse('makeReports:add-assessment',kwargs={'report':self.rpt.pk}),fD)
        num = AssessmentVersion.objects.filter(
            slo=slo,
            ).count()
        self.assertGreaterEqual(num,1)
class ImportAssessmentPageTest(ReportSetupTest):
    """
    Tests the import assessment page
    """
    def setUp(self):
        """
        Creates an assessment to import and SLO to import to
        """
        super().setUp()
        self.slo = baker.make("SLOInReport",report=self.rpt)
        self.rpt2 = baker.make("Report", degreeProgram=self.rpt.degreeProgram,year=2019)
        self.slo2 = baker.make("SLOInReport",report=self.rpt2)
        self.assess = baker.make("AssessmentVersion",slo=self.slo2,report=self.rpt2)
    def test_view(self):
        """
        Test that the page exists
        """
        response = self.client.get(reverse('makeReports:import-assessment',kwargs={'report':self.rpt.pk})+"?year=2019&dp="+str(self.slo2.report.degreeProgram.pk)+"&slo="+str(self.slo2.pk))
        self.assertEquals(response.status_code,200)
        self.assertContains(response,"mport")
    def test_post(self):
        """
        Tests that posting data imports assessment
        """
        fD = {
            'assessment': self.assess.pk,
            'slo': self.slo.pk
        }
        self.client.post(reverse('makeReports:import-assessment',kwargs={'report':self.rpt.pk})+"?year=2019&dp="+str(self.slo2.report.degreeProgram.pk)+"&slo="+str(self.slo2.pk),fD)
        num = AssessmentVersion.objects.filter(report=self.rpt).count()
        self.assertGreaterEqual(num, 1)
class ImportAssessmentPageTestRecipe(ImportAssessmentPageTest):
    """
    Tests the import assessment page with recipe based models
    """
    def setUp(self):
        """
        Creates an assessment to import and SLO to import to from recipes
        """
        super().setUp()
        self.slo = baker.make_recipe("makeReports.sloInReport",report=self.rpt)
        self.rpt2 = baker.make_recipe("makeReports.report", degreeProgram=self.rpt.degreeProgram,year=2019)
        self.slo2 = baker.make_recipe("makeReports.sloInReport",report=self.rpt2)
        self.assess = baker.make_recipe("makeReports.assessmentVersion",slo=self.slo2,report=self.rpt2)
class EditAssessmentTest(ReportSetupTest):
    """
    Tests the edit and delete assessment pages
    """
    def setUp(self):
        """
        Sets up assessments to edit
        """
        super(EditAssessmentTest,self).setUp()
        self.assessN = baker.make("AssessmentVersion",report=self.rpt, assessment__numberOfUses=1)
        self.assessN.assessment.numberOfUses = 1
        self.assessN.assessment.save()
        self.shareAssess = baker.make("Assessment", numberOfUses = 2)
        self.assessO = baker.make("AssessmentVersion",report=self.rpt, assessment=self.shareAssess)
        self.assessO2 = baker.make("AssessmentVersion",report=self.rpt, assessment=self.shareAssess)
        self.shareAssess.numberOfUses=2
        self.shareAssess.save()
    def test_view_new(self):
        """
        Tests that the edit new assessment page exists
        """
        response = getWithReport('edit-new-assessment',self,{'assessIR':self.assessN.pk},"")
        self.assertEquals(response.status_code,200)
    def test_view_new_edit_DNE(self):
        """
        Tests the edit new assessment page returns 404 when the object does not exist
        """
        response = getWithReport('edit-new-assessment',self,{'assessIR':399},"")
        self.assertEquals(response.status_code,404)
    def test_view_old(self):
        """
        Tests that the edit imported assessment page exists
        """
        response = getWithReport('edit-impt-assessment',self,{'assessIR':self.assessO.pk},"")
        self.assertEquals(response.status_code,200)
    def test_view_new_DNE(self):
        """
        Tests the imported assessment page returns 404 when the object does not exist
        """
        response = getWithReport('edit-impt-assessment',self,{'assessIR':399},"")
        self.assertEquals(response.status_code,404)
    def test_post_new(self):
        """
        Tests that posting information to the edit new assessment page work
        """
        slo = baker.make("SLOInReport", report=self.rpt)
        fD = {
            'slo': slo.pk,
            'title': 'Final performance',
            'description': 'Students will write a musical',
            'domain': ["Pe","Pr"],
            'directMeasure':True,
            'finalTerm':True,
            'where': 'During SPEECH 5070',
            'allStudents': True,
            'sampleDescription':'Every student',
            'frequencyChoice': FREQUENCY_CHOICES[0][0],
            'frequency':'Every week',
            'threshold':'At least a 90th percentile',
            'target':74
        }
        postWithReport('edit-new-assessment',self,{'assessIR':self.assessN.pk},"",fD)
        self.assessN.refresh_from_db()
        self.assertEquals(self.assessN.assessment.title, 'Final performance')
        self.assertEquals(self.assessN.target,74)
    def test_post_new_frequency_choice_fail(self):
        """
        Tests that posting that is not a valid frequency choice fails
        """
        slo = baker.make_recipe("makeReports.sloInReport", report=self.rpt)
        fD = {
            'slo': slo.pk,
            'title': 'Report',
            'description': 'A report comparing poetry',
            'domain': ["Pe","Pr"],
            'directMeasure':True,
            'finalTerm':True,
            'where': 'ENGL 3050',
            'allStudents': True,
            'sampleDescription':'dsd',
            'frequencyChoice': 'this is not a valid choice',
            'frequency':'',
            'threshold':'At least 85 percent',
            'target':64
        }
        response = postWithReport('edit-new-assessment',self,{'assessIR':self.assessN.pk},"",fD)
        self.assessN.refresh_from_db()
        self.assertNotEqual(self.assessN.assessment.title, 'Report')
        self.assertNotEqual(self.assessN.target,64)
        self.assertNotEqual(response.status_code,302)
    def test_post_impt_fails(self):
        """
        Tests that posting too much information to the edit imported assessment page fails
        """
        slo = baker.make("SLOInReport", report=self.rpt)
        fD = {
            'slo': slo.pk,
            'title': 'Literature review and publish',
            'description': 'Students will compare several pieces of literature.',
            'domain': ["Pe","Pr"],
            'directMeasure':True,
            'finalTerm':True,
            'where': 'a place',
            'allStudents': True,
            'sampleDescription':'',
            'frequencyChoice': FREQUENCY_CHOICES[0][0],
            'frequency':'',
            'threshold':'At least 80 percent by rubric',
            'target':34
        }
        postWithReport('edit-impt-assessment',self,{'assessIR':self.assessO.pk},"",fD)
        self.assessO.refresh_from_db()
        self.assertNotEquals(self.assessO.assessment.title, 'Literature review and publish')
    def test_post_impt(self):
        """
        Tests that posting the correct information to the edit imported assessment page works
        """
        slo = baker.make("SLOInReport", report=self.rpt)
        fD = {
            'slo': slo.pk,
            'description': 'Students will analyze biological reports',
            'finalTerm':True,
            'where': 'BIOL 3909',
            'allStudents': True,
            'sampleDescription':'All students',
            'frequencyChoice': FREQUENCY_CHOICES[0][0],
            'frequency':'Every spring and summer',
            'threshold':'With 90 degrees of accuracy',
            'target':34
        }
        postWithReport('edit-impt-assessment',self,{'assessIR':self.assessO.pk},"",fD)
        self.assessO.refresh_from_db()
        self.assertEquals(self.assessO.frequency, 'Every spring and summer')
    def test_delete_new(self):
        """
        Tests that deleting a new assessment deletes the in-report and overarching version
        """
        pk = self.assessN.pk
        aPk = self.assessN.assessment.pk
        self.assessN.assessment.numberOfUses = 1
        self.assessN.assessment.save()
        r = getWithReport('delete-new-assessment',self,{'pk':self.assessN.pk},"")
        self.assertEquals(r.status_code,200)
        postWithReport('delete-new-assessment',self,{'pk':self.assessN.pk},"",{})
        num = AssessmentVersion.objects.filter(pk=pk).count()
        self.assertEquals(num,0)
        num = Assessment.objects.filter(pk=aPk).count()
        self.assertEquals(num,0)
    def test_delete_new_DNE(self):
        """
        Tests the delete (new) assessment page returns 404 when the object does not exist
        """
        response = getWithReport('delete-new-assessment',self,{'pk':4242},"")
        self.assertEquals(response.status_code,404)
    def test_delete_old(self):
        """
        Tests that deleting an imported assessment deletes only the in-report version
        """
        pk = self.assessO.pk
        aPk = self.assessO.assessment.pk
        self.assessO.slo.numberOfAssess = 1
        self.assessO.slo.save()
        self.assessO.assessment.numberOfUses = 2
        self.assessO.assessment.save()
        r = getWithReport('delete-impt-assessment',self,{'pk':self.assessO.pk},"")
        self.assertEquals(r.status_code,200)
        postWithReport('delete-impt-assessment',self,{'pk':self.assessO.pk},"",{})
        num = AssessmentVersion.objects.filter(pk=pk).count()
        self.assertEquals(num,0)
        num = Assessment.objects.filter(pk=aPk).count()
        self.assertEquals(num,1)
    def test_delete_old_DNE(self):
        """
        Tests the delete (imported) assessment page returns 404 when the object does not exist
        """
        response = getWithReport('delete-impt-assessment',self,{'pk':4242},"")
        self.assertEquals(response.status_code,404)
class EditAssessmentRecipeTest(EditAssessmentTest):
    """
    Tests the edit assessment pages with recipe based models
    """
    def setUp(self):
        """
        Sets up the assessments from recipes
        """
        super().setUp()
        self.assessN = baker.make_recipe("makeReports.assessmentVersion",report=self.rpt, assessment__numberOfUses=1)
        self.assessN.assessment.numberOfUses =1
        self.assessN.assessment.save()
        self.shareAssess = baker.make_recipe("makeReports.assessment", numberOfUses = 2)
        self.assessO = baker.make_recipe("makeReports.assessmentVersion",report=self.rpt, assessment=self.shareAssess)
        self.assessO2 = baker.make_recipe("makeReports.assessmentVersion",report=self.rpt, assessment=self.shareAssess)
class AssessmentSupplementTest(ReportSetupTest):
    """
    Tests that supplement pages all exist
    """
    def setUp(self):
        """
        Creates an assessment and supplement
        """
        super(AssessmentSupplementTest,self).setUp()
        self.a = baker.make("AssessmentVersion", report=self.rpt)
        self.a2 = baker.make("AssessmentVersion",report=self.rpt)
        self.sup = baker.make("AssessmentSupplement")
        self.a.supplements.add(self.sup)
        self.sup2 = baker.make("AssessmentSupplement")
        self.a2.supplements.add(self.sup2)

    def test_upload(self):
        """
        Checks that the upload assessment page exists
        """
        response = getWithReport('assessment-supplement-upload',self,{'assessIR':self.a.pk},"")
        self.assertEquals(response.status_code,200)
    def test_upload_DNE(self):
        """
        Tests the upload assessment supplement page returns 404 when the object does not exist
        """
        response = getWithReport('assessment-supplement-upload',self,{'assessIR':4242},"")
        self.assertEquals(response.status_code,404)
    def test_import(self):
        """
        Checks that the import supplement page exists
        """
        response = getWithReport('assessment-supplement-import',self, {'assessIR':self.a.pk},"?year="+str(self.rpt.year)+"&dp="+str(self.rpt.degreeProgram.pk))
        self.assertEquals(response.status_code,200)
    def test_delete(self):
        """
        Checks that the delete supplement page exists
        """
        response = getWithReport('delete-supplement',self,{'assessIR':self.a.pk,'pk':self.sup.pk},"")
        self.assertEquals(response.status_code,200)
    def test_delete_DNE(self):
        """
        Tests the delete assessment supplement page returns 404 when the object does not exist
        """
        response = getWithReport('delete-supplement',self,{'assessIR':4242,'pk':8842},"")
        self.assertEquals(response.status_code,404)
    def test_delete_post(self):
        """
        Checks that posting to delete works
        """
        pk = self.sup.pk
        postWithReport('delete-supplement',self,{'assessIR':self.a.pk,'pk':self.sup.pk},"", {})
        num = AssessmentSupplement.objects.filter(pk=pk).count()
        self.assertEquals(num,0)
class AssessmentSupplementTestRecipe(AssessmentSupplementTest):
    """
    Tests that the supplement pages all exist using recipe-based models
    """
    def setUp(self):
        """
        Creates an assessment from the recipe and creates supplements
        """
        super().setUp()
        self.a = baker.make_recipe("makeReports.assessmentVersion", report=self.rpt)
        self.a2 = baker.make_recipe("makeReports.assessmentVersion",report=self.rpt)
        self.sup = baker.make("AssessmentSupplement")
        self.a.supplements.add(self.sup)
        self.sup2 = baker.make("AssessmentSupplement")
        self.a2.supplements.add(self.sup2)    




        
