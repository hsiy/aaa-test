"""
Tests relating to the grading views
"""
from django.urls import reverse
from model_bakery import baker
from .test_basicViews import ReportAACSetupTest

class GradingSectionsTest(ReportAACSetupTest):
    """
    Tests that grading sections works as expected
    """
    def setUp(self):
        """
        Sets-up a rubric and rubric item in each section
        """
        super().setUp()
        self.r = baker.make("Rubric")
        self.rub = baker.make("GradedRubric",rubricVersion=self.r)
        self.rInG = baker.make("RubricItem",rubricVersion=self.r,section=1)
        self.rInG2 = baker.make("RubricItem",rubricVersion=self.r,section=2)
        self.rInG3 = baker.make("RubricItem",rubricVersion=self.r,section=3)
        self.rInG4 = baker.make("RubricItem",rubricVersion=self.r,section=4)
        self.rI = baker.make("GradedRubricItem", rubric=self.rub, item=self.rInG)
        self.rI2 = baker.make("GradedRubricItem", rubric=self.rub, item=self.rInG2)
        self.rI3 = baker.make("GradedRubricItem", rubric=self.rub, item=self.rInG3)
        self.rI4 = baker.make("GradedRubricItem", rubric=self.rub, item=self.rInG4)
        self.rpt.rubric = self.rub
        self.rpt.save()
    def test_entry(self):
        """
        Tests the grading entry page exists
        """
        resp = self.client.get(reverse('makeReports:grade-entry',kwargs={
            'report':self.rpt.pk
        }))
        self.assertEquals(resp.status_code,200)
    def test_sec1_get(self):
        """
        Tests that the section 1 grading page works as expected
        """
        resp = self.client.get(reverse('makeReports:grade-sec1',kwargs={'report':self.rpt.pk}))
        self.assertContains(resp,self.rI.item.text)
        self.assertContains(resp,self.rI.item.DMEtext)
        self.assertContains(resp,self.rI.item.MEtext)
        self.assertContains(resp,self.rI.item.EEtext)
    def test_sec1_post(self):
        """
        Tests that the section 1 grading page works as expected when posting grade
        """
        fieldName = 'rI'+str(self.rInG.pk)
        resp = self.client.post(reverse('makeReports:grade-sec1',kwargs={'report':self.rpt.pk}),{
            fieldName:"ME",
            'section_comment':'fsfkjllaskdfls'
        })
        self.assertEquals(resp.status_code,302)
        self.rI.refresh_from_db()
        self.rub.refresh_from_db()
        self.assertEquals(self.rI.grade,"ME")
        self.assertEquals(self.rub.section1Comment,'fsfkjllaskdfls')
    def test_sec1_post_tooLong(self):
        """
        Tests that section 1 grading fails with too long of comment
        """
        fieldName = 'rI'+str(self.rInG.pk)
        reallyLong = "This needs more improvement."*1000
        resp = self.client.post(reverse('makeReports:grade-sec1',kwargs={'report':self.rpt.pk}),{
            fieldName:"ME",
            'section_comment':reallyLong
        })
        self.assertNotEquals(resp.status_code,302)
    def test_sec2_get(self):
        """
        Tests that the section 2 grading page works as expected
        """
        resp = self.client.get(reverse('makeReports:grade-sec2',kwargs={'report':self.rpt.pk}))
        self.assertContains(resp,self.rI2.item.text)
        self.assertContains(resp,self.rI2.item.DMEtext)
        self.assertContains(resp,self.rI2.item.MEtext)
        self.assertContains(resp,self.rI2.item.EEtext)
    def test_sec2_post(self):
        """
        Tests that the section 2 grading page works as expected when posting grade
        """
        fieldName = 'rI'+str(self.rInG2.pk)
        self.client.post(reverse('makeReports:grade-sec2',kwargs={'report':self.rpt.pk}),{
            fieldName:"DNM",
            'section_comment':'More students should take assessment 2.'
        })
        self.rI2.refresh_from_db()
        self.rub.refresh_from_db()
        self.assertEquals(self.rI2.grade,"DNM")
        self.assertEquals(self.rub.section2Comment,'More students should take assessment 2.')
    def test_sec2_post_missingComment(self):
        """
        Tests that the section 2 grading page works as expected when optional section comment is empty
        """
        fieldName = 'rI'+str(self.rInG2.pk)
        self.client.post(reverse('makeReports:grade-sec2',kwargs={'report':self.rpt.pk}),{
            fieldName:"DNM",
            'section_comment':''
        })
        self.rI2.refresh_from_db()
        self.assertEquals(self.rI2.grade,"DNM")
    def test_sec3_get(self):
        """
        Tests that the section 1 grading page works as expected
        """
        resp = self.client.get(reverse('makeReports:grade-sec3',kwargs={'report':self.rpt.pk}))
        self.assertContains(resp,self.rI3.item.text)
        self.assertContains(resp,self.rI3.item.DMEtext)
        self.assertContains(resp,self.rI3.item.MEtext)
        self.assertContains(resp,self.rI3.item.EEtext)
    def test_sec3_post(self):
        """
        Tests that the section 3 grading page works as expected when posting grade
        """
        fieldName = 'rI'+str(self.rInG3.pk)
        self.client.post(reverse('makeReports:grade-sec3',kwargs={'report':self.rpt.pk}),{
            fieldName: "MC",
            'section_comment':'More students should take assessment 2 so there can be more data.'
        })
        self.rI3.refresh_from_db()
        self.rub.refresh_from_db()
        self.assertEquals(self.rI3.grade,"MC")
        self.assertEquals(self.rub.section3Comment,'More students should take assessment 2 so there can be more data.')
    def test_sec4_get(self):
        """
        Tests that the section 1 grading page works as expected
        """
        resp = self.client.get(reverse('makeReports:grade-sec4',kwargs={'report':self.rpt.pk}))
        self.assertContains(resp,self.rI4.item.text)
        self.assertContains(resp,self.rI4.item.DMEtext)
        self.assertContains(resp,self.rI4.item.MEtext)
        self.assertContains(resp,self.rI4.item.EEtext)
    def test_sec4_post(self):
        """
        Tests that the section 4 grading page works as expected when posting grade
        """
        fieldName = 'rI'+str(self.rInG4.pk)
        self.client.post(reverse('makeReports:grade-sec4',kwargs={'report':self.rpt.pk}),{
            fieldName:"ME",
            'section_comment':'Spend more time discussing results with the stakeholders.'
        })
        self.rI4.refresh_from_db()
        self.rub.refresh_from_db()
        self.assertEquals(self.rI4.grade,"ME")
        self.assertEquals(self.rub.section4Comment,'Spend more time discussing results with the stakeholders.')
    def test_comment(self):
        """
        Tests that the overall comment page interacts with the database as expected
        """
        rub = baker.make("GradedRubric")
        self.rpt.rubric = rub
        self.rpt.save()
        self.rpt.refresh_from_db()
        r = self.client.get(reverse('makeReports:grade-comment',kwargs={'report':self.rpt.pk}))
        self.assertEquals(r.status_code,200)
        r = self.client.post(reverse('makeReports:grade-comment',kwargs={'report':self.rpt.pk}),{
            'text':'comm test'
        })
        self.assertEquals(self.rpt.rubric.generalComment,'comm test')
    
    def test_review_get(self):
        """
        Ensures that the the grading preview page exists
        """
        r = self.client.get(reverse('makeReports:rub-review',kwargs={
            'report':self.rpt.pk
        }))
        self.assertEquals(r.status_code,200)
class GradingSectionsTestRecipe(GradingSectionsTest):
    """
    Tests the grading sections using recipe based models
    """
    def setUp(self):
        """
        Sets-up a rubric and rubric item in each section using recipes
        """
        super().setUp()
        self.rub = baker.make_recipe("makeReports.gradedRubric",rubricVersion=self.r)
        self.rInG = baker.make_recipe("makeReports.rubricItem",rubricVersion=self.r,section=1)
        self.rInG2 = baker.make_recipe("makeReports.rubricItem",rubricVersion=self.r,section=2)
        self.rInG3 = baker.make_recipe("makeReports.rubricItem",rubricVersion=self.r,section=3)
        self.rInG4 = baker.make_recipe("makeReports.rubricItem",rubricVersion=self.r,section=4)
        self.rI = baker.make_recipe("makeReports.gradedRubricItem", rubric=self.rub, item=self.rInG)
        self.rI2 = baker.make_recipe("makeReports.gradedRubricItem", rubric=self.rub, item=self.rInG2)
        self.rI3 = baker.make_recipe("makeReports.gradedRubricItem", rubric=self.rub, item=self.rInG3)
        self.rI4 = baker.make_recipe("makeReports.gradedRubricItem", rubric=self.rub, item=self.rInG4)
        self.rpt.rubric = self.rub
        self.rpt.save()
