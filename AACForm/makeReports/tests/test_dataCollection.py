"""
Tests related to testing data collection entry views
"""
from django.urls import reverse
from makeReports.models import AssessmentAggregate, AssessmentData, ResultCommunicate, SLOStatus
from model_bakery import baker
from .test_basicViews import ReportAACSetupTest
from makeReports.choices import SLO_STATUS_CHOICES

class DataCollectionMainTableTests(ReportAACSetupTest):
    """
    Collection of tests that directly interact with the main data table
    """
    def setUp(self):
        """
        Creates an assessment to test with
        """
        super().setUp()
        self.slo = baker.make("SLOInReport", report=self.rpt)
        self.assess = baker.make("AssessmentVersion", report=self.rpt, slo=self.slo)
        self.assess2 = baker.make("AssessmentVersion",report=self.rpt, slo=self.slo)
    def test_datasummary(self):
        """
        Tests the summary page exists with expected content
        """
        resp = self.client.get(reverse('makeReports:data-summary',kwargs={
            'report':self.rpt.pk
        }))
        self.assertContains(resp,self.assess.assessment.title)
        self.assertContains(resp,"ata")
    def test_createDataRow(self):
        """
        Tests the ability to post data to create a new data row
        """
        r = self.client.get(reverse('makeReports:add-data-collection',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk
        }))
        self.assertEquals(r.status_code,200)
        resp = self.client.post(reverse('makeReports:add-data-collection',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk
        }),{
            'dataRange':'Fall 2017',
            'numberStudents':20,
            'overallProficient':75
        })
        num = AssessmentData.objects.filter(
            assessmentVersion = self.assess,
            dataRange = "Fall 2017",
            numberStudents = 20,
            overallProficient = 75
        ).count()
        self.assertEquals(num,1)
        self.assertEquals(resp.status_code,302)
    def test_createDataRow_DNE(self):
        """
        Tests the create data row page returns 404 when the object does not exist
        """
        r = self.client.get(reverse('makeReports:add-data-collection',kwargs={
            'report':self.rpt.pk,
            'assessment':342
        }))
        self.assertEquals(r.status_code,404)
    def test_createDataRow_noDataRange(self):
        """
        Tests the form fails when there is not a data range
        """
        resp = self.client.post(reverse('makeReports:add-data-collection',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk
        }),{
            'numberStudents':20,
            'overallProficient':75
        })
        self.assertNotEquals(resp.status_code,302)
    def test_createDataRow_negativeInteger(self):
        """
        Tests the form fails when a negative number of students is entered
        """
        resp = self.client.post(reverse('makeReports:add-data-collection',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk
        }),{
            'numberStudents':-20,
            'overallProficient':75
        })
        self.assertNotEquals(resp.status_code,302)
    def test_createDataRow_nonIntegerProficient(self):
        """
        Tests the form fails when a fractional percentage is entered
        """
        resp = self.client.post(reverse('makeReports:add-data-collection',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk
        }),{
            'numberStudents':20,
            'overallProficient':75.34
        })
        self.assertNotEquals(resp.status_code,302)
    def test_multipleMeasuresData(self):
        """
        Tests that mutliple measures for an SLO both appear in the table
        """
        d1 = baker.make("AssessmentData",assessmentVersion=self.assess,overallProficient=34)
        d2 = baker.make("AssessmentData", assessmentVersion = self.assess2,overallProficient=34)
        resp = self.client.get(reverse('makeReports:data-summary',kwargs={
            'report':self.rpt.pk
        }))
        self.assertContains(resp,d1.dataRange)
        self.assertContains(resp,d2.dataRange)
        self.assertContains(resp,d1.numberStudents)
        self.assertContains(resp,d2.numberStudents)
        self.assertContains(resp,d1.overallProficient)
        self.assertContains(resp,d2.overallProficient)
    def test_datarowFromAssess(self):
        """
        Tests the create data row form assessment page works and redirects to the assessment summary page
        """
        r = self.client.get(reverse('makeReports:add-data-collection-assess',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk
        }))
        self.assertEquals(r.status_code,200)
        resp = self.client.post(reverse('makeReports:add-data-collection-assess',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk
        }),{
            'dataRange':'Fall 2019',
            'numberStudents':21,
            'overallProficient':76
        })
        num = AssessmentData.objects.filter(
            assessmentVersion = self.assess,
            dataRange = "Fall 2019",
            numberStudents = 21,
            overallProficient = 76
        ).count()
        self.assertEquals(num,1)
        self.assertRedirects(resp,reverse('makeReports:assessment-summary',kwargs={'report':self.rpt.pk}))
    def test_createDataRow_fromAssessment_DNE(self):
        """
        Tests the create data row page returns 404 when the object does not exist
        """
        r = self.client.get(reverse('makeReports:add-data-collection-assess',kwargs={
            'report':self.rpt.pk,
            'assessment':342
        }))
        self.assertEquals(r.status_code,404)
    def test_datarowFromAssess_noproficient(self):
        """
        Tests the create data row page from assessment fails there is not a proficiency number
        """
        resp = self.client.post(reverse('makeReports:add-data-collection-assess',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk
        }),{
            'dataRange':'Fall 2019',
            'numberStudents':21,
        })
        self.assertNotEquals(resp.status_code,302)
    def test_editDataRow(self):
        """
        Test that the page to edit data row actually edits the data row
        """
        d = baker.make("AssessmentData",assessmentVersion=self.assess,overallProficient=34)
        pk = d.pk
        resp = self.client.get(reverse('makeReports:edit-data-collection',kwargs={
            'report':self.rpt.pk,
            'dataCollection': d.pk
        }))
        self.assertEquals(resp.status_code,200)
        resp = self.client.post(reverse('makeReports:edit-data-collection',kwargs={
            'report':self.rpt.pk,
            'dataCollection': d.pk
        }),{
            'dataRange':'Fall 2019',
            'numberStudents':31,
            'overallProficient':86
        })
        num = AssessmentData.objects.filter(
            assessmentVersion = self.assess,
            dataRange = "Fall 2019",
            numberStudents = 31,
            overallProficient = 86,
            pk = pk
        ).count()
        self.assertEquals(num,1)
    def test_editDataRow_DNE(self):
        """
        Tests the edit data row page returns 404 when the object does not exist
        """
        r = self.client.get(reverse('makeReports:edit-data-collection',kwargs={
            'report':self.rpt.pk,
            'dataCollection':423
        }))
        self.assertEquals(r.status_code,404)
    def test_deleteDataRow(self):
        """
        Tests that the page to the delete page actually deletes the data row
        """
        d = baker.make("AssessmentData",assessmentVersion=self.assess,overallProficient=34)
        pk = d.pk
        resp = self.client.get(reverse('makeReports:delete-data-collection',kwargs={
            'report':self.rpt.pk,
            'pk':d.pk
        }))
        self.assertEquals(resp.status_code,200)
        resp = self.client.post(reverse('makeReports:delete-data-collection',kwargs={
            'report':self.rpt.pk,
            'pk':d.pk
        }))
        num = AssessmentData.objects.filter(pk=pk).count()
        self.assertEquals(num,0)
    def test_deleteDataRow_DNE(self):
        """
        Tests the delete data row page returns 404 when the object does not exist
        """
        r = self.client.get(reverse('makeReports:delete-data-collection',kwargs={
            'report':self.rpt.pk,
            'pk': 4324
        }))
        self.assertEquals(r.status_code,404)
    def test_addAgg(self):
        """
        Tests adding a new AssessmentAggregate
        """
        self.assess.target = 75
        self.assess.save()
        r = self.client.get(reverse('makeReports:data-agg-create',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk
        }))
        self.assertEquals(r.status_code,200)
        self.client.post(reverse('makeReports:data-agg-create',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk
        }),{
            'aggregate_proficiency': 80
        })
        num = AssessmentAggregate.objects.filter(assessmentVersion=self.assess,aggregate_proficiency=80,met=True).count()
        self.assertEquals(num,1)
    def test_addAggNotMet(self):
        """
        Tests adding a new assessment aggregate where the target is not met
        """
        self.assess.target = 95
        self.assess.save()
        resp = self.client.get(reverse('makeReports:data-agg-create',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk
        }))
        self.assertEquals(resp.status_code,200)
        resp = self.client.post(reverse('makeReports:data-agg-create',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk
        }),{
            'aggregate_proficiency': 80
        })
        num = AssessmentAggregate.objects.filter(assessmentVersion=self.assess,aggregate_proficiency=80,met=False).count()
        self.assertEquals(num,1)
    def test_addAggJustMet(self):
        """
        Tests adding an assessment aggregate where the target is just met
        """
        self.assess.target = 80
        self.assess.save()
        self.client.post(reverse('makeReports:data-agg-create',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk
        }),{
            'aggregate_proficiency': 80
        })
        num = AssessmentAggregate.objects.filter(assessmentVersion=self.assess,aggregate_proficiency=80,met=True).count()
        self.assertEquals(num,1)
    def test_editAgg(self):
        """
        Tests the page to view to edit assessment aggregate
        """
        self.assess.target = 80
        self.assess.save()
        agg = baker.make("AssessmentAggregate",assessmentVersion=self.assess, aggregate_proficiency=60, met=False)
        resp = self.client.get(reverse('makeReports:data-agg-edit',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk,
            'pk':agg.pk
        }))
        self.assertEquals(resp.status_code,200)
        resp = self.client.post(reverse('makeReports:data-agg-edit',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk,
            'pk':agg.pk
        }),{
            'aggregate_proficiency':85
        })
        num = AssessmentAggregate.objects.filter(aggregate_proficiency=85,pk=agg.pk,met=True).count()
        self.assertEquals(num,1)   
    def test_editAgg_DNE(self):
        """
        Tests the edit aggregate page returns 404 when the object does not exist
        """
        r = self.client.get(reverse('makeReports:data-agg-edit',kwargs={
            'report':self.rpt.pk,
            'assessment':self.assess.pk,
            'pk': 834
        }))
        self.assertEquals(r.status_code,404) 
class DataCollectionMainTableTestsRecipe(DataCollectionMainTableTests):
    """
    Collection of tests that directly interact with the main data table using recipes
    """
    def setUp(self):
        """
        Creates an assessment to test with
        """
        super().setUp()
        self.slo = baker.make_recipe("makeReports.sloInReport", report=self.rpt)
        self.assess = baker.make_recipe("makeReports.assessmentVersion", report=self.rpt, slo=self.slo)
        self.assess2 = baker.make_recipe("makeReports.assessmentVersion",report=self.rpt, slo=self.slo)
class DataCollectionExtrasTests(ReportAACSetupTest):
    """
    Tests views auxillary to the main table, but part of data collection
    """
    def setUp(self):
        """
        Creates assessments and data to test with
        """
        super().setUp()
        self.slo = baker.make("SLOInReport", report=self.rpt)
        self.assess = baker.make("AssessmentVersion", report=self.rpt, slo=self.slo)
        self.assess2 = baker.make("AssessmentVersion",report=self.rpt, slo=self.slo)
    def test_NewSLOStatus(self):
        """
        Tests the creation of a new SLO Status
        """
        resp = self.client.get(reverse('makeReports:add-slo-status',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk
        }))
        self.assertEquals(resp.status_code,200)
        resp = self.client.post(reverse('makeReports:add-slo-status',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk
        }),{
            'status':SLO_STATUS_CHOICES[0][0]
        })
        num = SLOStatus.objects.filter(
            status=SLO_STATUS_CHOICES[0][0],
            sloIR=self.slo).count()
        self.assertEquals(num,1)
    def test_newSLOStatus_DNE(self):
        """
        Tests the new SLO status page returns 404 when the SLO does not exist
        """
        r = self.client.get(reverse('makeReports:add-slo-status',kwargs={
            'report':self.rpt.pk,
            'slopk':423
        }))
        self.assertEquals(r.status_code,404) 
    def test_NewSLOStatus_invalid(self):
        """
        Tests the creation of a new SLO status handles invalid options
        """
        resp = self.client.post(reverse('makeReports:add-slo-status',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk
        }),{
            'status':'not a status'
        })

        self.assertNotEquals(resp.status_code,302)

    def test_editSLOStatus(self):
        """
        Tests the editing of an SLO Status
        """
        stat = baker.make("SLOStatus",sloIR=self.slo,status=SLO_STATUS_CHOICES[1][0])
        resp = self.client.get(reverse('makeReports:edit-slo-status',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk,
            'statuspk':stat.pk
        }))
        self.assertEquals(resp.status_code,200)
        resp = self.client.post(reverse('makeReports:edit-slo-status',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk,
            'statuspk':stat.pk
        }),{
            'status':SLO_STATUS_CHOICES[0][0]
        })
        stat.refresh_from_db()
        self.assertEquals(stat.status,SLO_STATUS_CHOICES[0][0])
    def test_editSLOStatus_DNE(self):
        """
        Tests the edit SLO status page returns 404 when the status does not exist
        """
        r = self.client.get(reverse('makeReports:edit-slo-status',kwargs={
            'report':self.rpt.pk,
            'slopk':self.slo.pk,
            'statuspk': 3842
        }))
        self.assertEquals(r.status_code,404)
    def test_newResultCommunicate(self):
        """
        Tests that adding new result communication description via posting to page works
        """
        resp = self.client.get(reverse('makeReports:add-result-communication',kwargs={
            'report':self.rpt.pk
        }))
        self.assertEquals(resp.status_code,200)
        resp = self.client.post(reverse('makeReports:add-result-communication',kwargs={
            'report':self.rpt.pk
        }),{
            'text':'testingtesttesttest'
        })
        num = ResultCommunicate.objects.filter(
            report=self.rpt,
            text='testingtesttesttest'
        ).count()
        self.assertEquals(num,1)
    def test_editResultCommunicate(self):
        """
        Tests that editing result communication description via posting works
        """
        rc = baker.make("ResultCommunicate",report=self.rpt)
        resp = self.client.get(reverse('makeReports:edit-result-communication',kwargs={
            'report':self.rpt.pk,
            'resultpk':rc.pk
        }))
        self.assertEquals(resp.status_code,200)
        resp = self.client.post(reverse('makeReports:edit-result-communication',kwargs={
            'report':self.rpt.pk,
            'resultpk':rc.pk
        }),{
            'text':'testingtesttesttest43'
        })
        num = ResultCommunicate.objects.filter(
            report=self.rpt,
            text='testingtesttesttest43',
            pk=rc.pk
        ).count()
        self.assertEquals(num,1)
    def test_editResultCommunicate_DNE(self):
        """
        Tests the edit result communicate page returns 404 when the text not exist
        """
        r = self.client.get(reverse('makeReports:edit-result-communication',kwargs={
            'report':self.rpt.pk,
            'resultpk':949
        }))
        self.assertEquals(r.status_code,404)
    def test_section3Comment(self):
        """
        Tests that the section 3 comment page works as expected
        """
        resp = self.client.get(reverse('makeReports:data-comment',kwargs={
            'report':self.rpt.pk
        }))
        self.assertEquals(resp.status_code,200)
        resp = self.client.post(reverse('makeReports:data-comment',kwargs={
            'report':self.rpt.pk
        }),{
            'text':'comm3332'
        })
        self.rpt.refresh_from_db()
        self.assertEquals(self.rpt.section3Comment,'comm3332')
    #Skipped supplement views since dealing with files is problematic
    


    




