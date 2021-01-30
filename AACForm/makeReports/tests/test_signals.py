"""
Tests relating to signals
"""
from django.test import TestCase
from makeReports.models import AssessmentAggregate, SLOStatus
from model_bakery import baker

class AggregateReceiverTests(TestCase):
    """
    Tests related to functions that run on AssessmentAggregate save
    """
    def setUp(self):
        """
        Setups an assessment
        """
        super().setUp()
        self.slo = baker.make("SLOInReport")
        self.aV = baker.make("AssessmentVersion", target=50,slo=self.slo)
    def test_oncreate_status(self):
        """
        Tests that statuses are created when assessment aggregates are
        """
        baker.make("AssessmentAggregate",assessmentVersion=self.aV,aggregate_proficiency=60,met=True)
        ss = SLOStatus.objects.filter(sloIR=self.slo).first()
        ss.refresh_from_db()
        self.assertEquals("Met",ss.status)
    def test_onsave_status(self):
        """
        Tests statuses are updated when assessment aggregates are updated
        """
        slo2 = baker.make("SLOInReport")
        self.aV.slo = slo2
        self.aV.save()
        aa = baker.make("AssessmentAggregate",assessmentVersion=self.aV,aggregate_proficiency=60,met=False)
        aa.aggregate_proficiency = 25
        aa.save()
        ss = SLOStatus.objects.filter(sloIR=slo2).first()
        ss.refresh_from_db()
        self.assertEquals("Not Met",ss.status)
    def test_onsave_agg(self):
        """
        Tests Aggregate is updated when data is
        """
        aV = baker.make("AssessmentVersion")
        data = baker.make("AssessmentData", assessmentVersion=aV,overallProficient=34)
        a = AssessmentAggregate.objects.get(assessmentVersion=aV)
        self.assertEquals(a.aggregate_proficiency,data.overallProficient)
        data.overallProficient=73
        data.save()
        a.refresh_from_db()
        self.assertEquals(a.aggregate_proficiency,data.overallProficient)
    
        

    
    
