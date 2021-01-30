"""
Tests related to testing views for entering decisions and actions
"""
from django.urls import reverse
from makeReports.models import DecisionsActions
from model_bakery import baker
from .test_basicViews import ReportSetupTest

class DecActViewsTest(ReportSetupTest):
    """
    Tests all views relating to decisions and actions
    """
    def setUp(self):
        """
        Create an SLO to input decisions/actions for
        """
        super().setUp()
        self.slo = baker.make("SLOInReport",report=self.rpt)
    def test_summary(self):
        """
        Tests that the summary page exists
        """
        resp = self.client.get(reverse('makeReports:decisions-actions-summary',kwargs={
            'report':self.rpt.pk
        }))
        self.assertContains(resp,'SLO')
    def test_addDecAct(self):
        """
        Tests adding a decision action via posting to the view
        """
        resp = self.client.get(reverse('makeReports:add-decisions-actions',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk
        }))
        self.assertEquals(resp.status_code, 200)
        resp = self.client.post(reverse('makeReports:add-decisions-actions',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk
        }),{
            'text':'testingtestingtest'
        })
        num = DecisionsActions.objects.filter(text='testingtestingtest',sloIR=self.slo).count()
        self.assertEquals(num,1)
    def test_addDecAct_DNE(self):
        """
        Tests the add decision/action page returns 404 when the SLO not exist
        """
        r = self.client.get(reverse('makeReports:add-decisions-actions',kwargs={
            'report':self.rpt.pk,
            'slopk':4324
        }))
        self.assertEquals(r.status_code,404)
    def test_addDecAct_toolong(self):
        """
        Tests that adding a decision/action with too long of text fails
        """
        resp = self.client.post(reverse('makeReports:add-decisions-actions',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk
        }),{
            'text':'xyz !'*800
        })
        self.assertNotEquals(resp.status_code,302)
    def test_addDecActSLO(self):
        """
        Tests that adding a decision action from SLO page redirects to SLO page
        """
        resp = self.client.get(reverse('makeReports:add-decisions-actions-slo',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk
        }))
        self.assertEquals(resp.status_code,200)
        resp = self.client.post(reverse('makeReports:add-decisions-actions-slo',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk
        }),{
            'text':'We will modify ENGL 4050 to have better support.'
        })
        num = DecisionsActions.objects.filter(text='We will modify ENGL 4050 to have better support.',sloIR=self.slo).count()
        self.assertEquals(num,1)
        self.assertRedirects(resp,reverse('makeReports:slo-summary',kwargs={
            'report':self.rpt.pk
        }))
    def test_addDecActSLO_DNE(self):
        """
        Tests the add decision/action from SLO summary page returns 404 when the SLO not exist
        """
        r = self.client.get(reverse('makeReports:add-decisions-actions-slo',kwargs={
            'report':self.rpt.pk,
            'slopk':424
        }))
        self.assertEquals(r.status_code,404)
    def test_addDecActSLO_missingtext(self):
        """
        Tests that missing the text when adding the decision/action fails
        """
        resp = self.client.post(reverse('makeReports:add-decisions-actions-slo',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk
        }),{
        })
        self.assertNotEquals(resp.status_code,302)
    def test_addDecActSLO_toolong(self):
        """
        Tests that too long of text fails
        """
        resp = self.client.post(reverse('makeReports:add-decisions-actions-slo',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk
        }),{
            'text':'Modifying the curriculum.'*500
        })
        self.assertNotEquals(resp.status_code,302)
    def test_editDecAct(self):
        """
        Tests that posting to view edits the decision/action text
        """
        dA = baker.make("DecisionsActions",sloIR=self.slo)
        resp=self.client.get(reverse('makeReports:edit-decisions-actions',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk,
            'pk':dA.pk
        }))
        self.assertEquals(resp.status_code,200)
        resp = self.client.post(reverse('makeReports:edit-decisions-actions',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk,
            'pk':dA.pk
        }),{
            'text':'We will meet with our stakeholders starting next week.'
        })
        dA.refresh_from_db()
        self.assertEquals(dA.text,'We will meet with our stakeholders starting next week.')
    def test_editDecActSLO_DNE(self):
        """
        Tests the edit decision/action page returns 404 when the dec/act not exist
        """
        r = self.client.get(reverse('makeReports:edit-decisions-actions',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk,
            'pk': 4329
        }))
        self.assertEquals(r.status_code,404)
    def test_editDecAct_toolong(self):
        """
        Tests that too long of text does not change the decision/action text
        """
        dA = baker.make("DecisionsActions",sloIR=self.slo, text="valid text")
        self.client.post(reverse('makeReports:edit-decisions-actions',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk,
            'pk':dA.pk
        }),{
            'text':'We will meet constantly with students.'*300
        })
        dA.refresh_from_db()
        self.assertEquals(dA.text,'valid text')

    def test_editDecActSLO(self):
        """
        Testing that the view edits the decision/action works and redirects as expected
        """
        dA = baker.make("DecisionsActions",sloIR=self.slo)
        resp = self.client.get(reverse('makeReports:edit-decisions-actions-slo',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk,
            'pk':dA.pk
        }))
        self.assertEquals(resp.status_code,200)
        resp = self.client.post(reverse('makeReports:edit-decisions-actions-slo',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk,
            'pk':dA.pk
        }),{
            'text':'The department will start to have study sessions available.'
        })
        dA.refresh_from_db()
        self.assertEquals(dA.text,'The department will start to have study sessions available.')
        self.assertRedirects(resp,reverse('makeReports:slo-summary',kwargs={
            'report':self.rpt.pk
        }))
    def test_addEditRedirect_add(self):
        """
        Tests the add/edit redirect redirects to add when there is not one already
        """
        slo2 = baker.make("SLOInReport",report=self.rpt)
        resp = self.client.get(reverse('makeReports:add-edit-redirect',kwargs={
            'report':self.rpt.pk,
            'slopk':slo2.pk
        }))
        self.assertRedirects(resp,reverse('makeReports:add-decisions-actions-slo',kwargs={
            'report':self.rpt.pk,
            'slopk':slo2.pk
        }))
    def test_addEditRedirect_edit(self):
        """
        Tests the add/edit redirect redirect to edit there is already one
        """
        slo2 = baker.make("SLOInReport",report=self.rpt)
        dA = baker.make("DecisionsActions",sloIR=slo2)
        resp = self.client.get(reverse('makeReports:add-edit-redirect',kwargs={
            'report':self.rpt.pk,
            'slopk':slo2.pk
        }))
        self.assertRedirects(resp,reverse('makeReports:edit-decisions-actions-slo',kwargs={
            'report':self.rpt.pk,
            'slopk':slo2.pk,
            'pk':dA.pk
        }))
    def test_section4comment(self):
        """
        Tests the section 4 comment works as expected when posted to
        """
        resp = self.client.get(reverse('makeReports:d-a-comment',kwargs={
            'report':self.rpt.pk
        }))
        self.assertEquals(resp.status_code,200)
        resp = self.client.post(reverse('makeReports:d-a-comment',kwargs={
            'report':self.rpt.pk
        }),{
            'text':'The department is working on meeting with the dean to discuss further changes.'
        })
        self.rpt.refresh_from_db()
        self.assertEquals(self.rpt.section4Comment,'The department is working on meeting with the dean to discuss further changes.')
class DecActViewsTestRecipe(DecActViewsTest):
    """
    Tests views relating to decisions and actions with recipe based SLO
    """
    def setUp(self):
        """
        Create an SLO to input decisions/actions for with recipe
        """
        super().setUp()
        self.slo = baker.make_recipe("makeReports.sloInReport",report=self.rpt)
    def test_editDecAct(self):
        """
        Tests that posting to view edits the decision/action text with recipe based model
        """
        dA = baker.make_recipe("makeReports.decisionsActions",sloIR=self.slo)
        self.client.post(reverse('makeReports:edit-decisions-actions',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk,
            'pk':dA.pk
        }),{
            'text':'Students will be required to take a research seminar during their sophomore year.'
        })
        dA.refresh_from_db()
        self.assertEquals(dA.text,'Students will be required to take a research seminar during their sophomore year.')
    def test_editDecAct_toolong(self):
        """
        Tests the decision/action does not update when the text is too long
        """
        dA = baker.make_recipe("makeReports.decisionsActions",sloIR=self.slo, text="all right text")
        self.client.post(reverse('makeReports:edit-decisions-actions',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk,
            'pk':dA.pk
        }),{
            'text':'The students will have to evaluate sources during the freshman intro course.'*500
        })
        dA.refresh_from_db()
        self.assertEquals(dA.text,'all right text')
    def test_editDecActSLO(self):
        """
        Testing that the view edits the decision/action works and redirects as expected with recipe base decision/action
        """
        dA = baker.make_recipe("makeReports.decisionsActions",sloIR=self.slo)
        resp = self.client.post(reverse('makeReports:edit-decisions-actions-slo',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk,
            'pk':dA.pk
        }),{
            'text':'The students will have to evaluate sources during the freshman intro course.'
        })
        dA.refresh_from_db()
        self.assertEquals(dA.text,'The students will have to evaluate sources during the freshman intro course.')
        self.assertRedirects(resp,reverse('makeReports:slo-summary',kwargs={
            'report':self.rpt.pk
        }))
    def test_addEditRedirect_add(self):
        """
        Tests the add/edit redirect redirects to add when there is not one already with recipe based SLO
        """
        slo2 = baker.make_recipe("makeReports.sloInReport",report=self.rpt)
        resp = self.client.get(reverse('makeReports:add-edit-redirect',kwargs={
            'report':self.rpt.pk,
            'slopk':slo2.pk
        }))
        self.assertRedirects(resp,reverse('makeReports:add-decisions-actions-slo',kwargs={
            'report':self.rpt.pk,
            'slopk':slo2.pk
        }))
    def test_addEditRedirect_edit(self):
        """
        Tests the add/edit redirect redirect to edit there is already one with recipe based model
        """
        slo2 = baker.make_recipe("makeReports.sloInReport",report=self.rpt)
        dA = baker.make_recipe("makeReports.decisionsActions",sloIR=slo2)
        resp = self.client.get(reverse('makeReports:add-edit-redirect',kwargs={
            'report':self.rpt.pk,
            'slopk':slo2.pk
        }))
        self.assertRedirects(resp,reverse('makeReports:edit-decisions-actions-slo',kwargs={
            'report':self.rpt.pk,
            'slopk':slo2.pk,
            'pk':dA.pk
        }))

