"""
Tests the APIs work as expected
"""
from django.urls import reverse
from makeReports.models import SLOStatus
from model_bakery import baker
from .test_basicViews import ReportAACSetupTest, NonAACTest

class APITesting(NonAACTest):
    """
    Contains tests that are APIs for the Javascript
    """
    def test_dept_by_col(self):
        """
        Tests that the API returns all departments within a college
        """
        col = baker.make("College")
        col2 = baker.make("College")
        dep1 = baker.make("Department",college=col)
        dep2 = baker.make("Department",college=col)
        depNo = baker.make("Department",college=col2)
        resp = self.client.get(reverse('makeReports:api-dept-by-col')+"?college="+str(col.pk))
        self.assertContains(resp,dep1.pk)
        self.assertContains(resp,dep1.name)
        self.assertContains(resp,dep2.pk)
        self.assertContains(resp,dep2.name)
        self.assertNotContains(resp,depNo.name)
    def test_dept_by_col_recipe(self):
        """
        Tests that the API returns all departments within a college suing recipes
        """
        col = baker.make_recipe("makeReports.college")
        col2 = baker.make_recipe("makeReports.college")
        dep1 = baker.make_recipe("makeReports.department",college=col)
        dep2 = baker.make_recipe("makeReports.department",college=col)
        depNo = baker.make_recipe("makeReports.department",college=col2)
        resp = self.client.get(reverse('makeReports:api-dept-by-col')+"?college="+str(col.pk))
        self.assertContains(resp,dep1.pk)
        self.assertContains(resp,dep1.name)
        self.assertContains(resp,dep2.pk)
        self.assertContains(resp,dep2.name)
        self.assertNotContains(resp,depNo.name)
    def test_SLOSuggestions(self):
        """
        Tests the SLO suggestions work as expected
        """
        resp = self.client.post(reverse('makeReports:api-slo-suggestions'),{
            'slo_text':'analyze analyze analyzing understand synthesize'
        })
        self.assertContains(resp,'Analysis')
    def test_prog_by_dept(self):
        """
        Tests the API returns programs within the department
        """
        dep = baker.make("Department")
        dep2 = baker.make("Department")
        prog = baker.make("DegreeProgram",department=dep)
        prog2 = baker.make("DegreeProgram",department=dep)
        progNo = baker.make("DegreeProgram",department=dep2)
        resp = self.client.get(reverse('makeReports:api-prog-by-dept')+"?department="+str(dep.pk))
        self.assertContains(resp,prog.name)
        self.assertContains(resp,prog.pk)
        self.assertContains(resp,prog2.name)
        self.assertContains(resp,prog2.pk)
        self.assertNotContains(resp,progNo.pk)
    def test_prog_by_dept_recipe(self):
        """
        Tests the API returns programs within the department with recipe based model
        """
        dep = baker.make_recipe("makeReports.department")
        dep2 = baker.make_recipe("makeReports.department")
        prog = baker.make_recipe("makeReports.degreeProgram",department=dep)
        prog2 = baker.make_recipe("makeReports.degreeProgram",department=dep)
        progNo = baker.make_recipe("makeReports.degreeProgram",department=dep2)
        resp = self.client.get(reverse('makeReports:api-prog-by-dept')+"?department="+str(dep.pk))
        self.assertContains(resp,prog.name)
        self.assertContains(resp,prog.pk)
        self.assertContains(resp,prog2.name)
        self.assertContains(resp,prog2.pk)
        self.assertNotContains(resp,progNo.pk)
    def test_slo_by_dp(self):
        """
        Tests that the API returns SLOs within the degree program
        """
        dp = baker.make("DegreeProgram")
        dp2 = baker.make("DegreeProgram")
        slo = baker.make("SLOInReport",report__degreeProgram=dp, report__year=2018)
        slo2 = baker.make("SLOInReport",report__degreeProgram=dp2,report__year=2018)
        resp = self.client.get(
            reverse('makeReports:api-slo-by-dp')+"?report__degreeProgram="+str(dp.pk)+"&report__year__gte=2016&report__year__lte=2019")
        self.assertContains(resp,slo.pk)
        self.assertNotContains(resp,slo2.pk)
    def test_slo_by_dp_recipe(self):
        """
        Tests that the API returns SLOs within the degree program using recipe based models
        """
        dp = baker.make_recipe("makeReports.degreeProgram")
        dp2 = baker.make_recipe("makeReports.degreeProgram")
        slo = baker.make_recipe("makeReports.sloInReport",report__degreeProgram=dp, report__year=2018)
        slo2 = baker.make_recipe("makeReports.sloInReport",report__degreeProgram=dp2,report__year=2018)
        resp = self.client.get(
            reverse('makeReports:api-slo-by-dp')+"?report__degreeProgram="+str(dp.pk)+"&report__year__gte=2016&report__year__lte=2019")
        self.assertContains(resp,slo.pk)
        self.assertNotContains(resp,slo2.pk)
    def test_assess_by_slo(self):
        """
        Tests the API collects assessments within the SLO, and that the results are unique by assessment
        """
        rept = baker.make("Report",year=2018)
        r2 = baker.make("Report",year=2016)
        slo = baker.make("SLO")
        sloIR = baker.make("SLOInReport",report=rept,slo=slo)
        sloIR2 = baker.make("SLOInReport",report=r2,slo=slo)
        slo2 = baker.make("SLO")
        sloIRNo = baker.make("SLOInReport",report__year=2019,slo=slo2)
        a = baker.make("Assessment")
        assess = baker.make("AssessmentVersion",assessment=a,report=rept,slo=sloIR)
        assess2 = baker.make("AssessmentVersion",assessment=a,report=r2,slo=sloIR2)
        assessNo = baker.make("AssessmentVersion",slo=sloIRNo)
        resp = self.client.get(reverse('makeReports:api-assess-by-slo')+"?slo__slo="+str(slo.pk)+"&report__year__gte=2015&report__year__lte=2019")
        self.assertContains(resp,assess.pk)
        self.assertNotContains(resp,assess2.pk)
        self.assertNotContains(resp,assessNo.pk)
    def test_assess_by_slo_recipe(self):
        """
        Tests the API collects assessments within the SLO, and that the results are unique by assessment using recipe based models
        """
        rept = baker.make_recipe("makeReports.report",year=2018)
        r2 = baker.make_recipe("makeReports.report",year=2016)
        slo = baker.make("SLO")
        sloIR = baker.make_recipe("makeReports.sloInReport",report=rept,slo=slo)
        sloIR2 = baker.make_recipe("makeReports.sloInReport",report=r2,slo=slo)
        slo2 = baker.make("SLO")
        sloIRNo = baker.make_recipe("makeReports.sloInReport",report__year=2019,slo=slo2)
        a = baker.make("Assessment")
        assess = baker.make_recipe("makeReports.assessmentVersion",assessment=a,report=rept,slo=sloIR)
        assess2 = baker.make_recipe("makeReports.assessmentVersion",assessment=a,report=r2,slo=sloIR2)
        assessNo = baker.make_recipe("makeReports.assessmentVersion",slo=sloIRNo)
        resp = self.client.get(reverse('makeReports:api-assess-by-slo')+"?slo__slo="+str(slo.pk)+"&report__year__gte=2015&report__year__lte=2019")
        self.assertContains(resp,assess.pk)
        self.assertNotContains(resp,assess2.pk)
        self.assertNotContains(resp,assessNo.pk)
    def test_api_new_graph_1(self):
        """
        Tests the status code the new graph API for type 1
        """
        department = baker.make("Department")
        program = baker.make("DegreeProgram",department=department)
        r = baker.make("Report", degreeProgram=program, year=2017)
        slo = baker.make("SLOInReport",report=r)
        assessHere = baker.make("AssessmentVersion",report=r,slo=slo)
        baker.make("AssessmentData",assessmentVersion=assessHere,overallProficient=93)
        data = {
            'report__degreeProgram__department': department.pk,
            'report__degreeProgram': program.pk,
            'report__year__gte': 2015,
            'report__year__lte': 2018,
            'decision': 1,
            'sloIR': slo.pk,
            'assess': assessHere.assessment.pk,
            'sloWeights': "{\""+str(slo.pk)+"\": 1}"
        }
        resp = self.client.post(reverse('makeReports:api-new-graph'),data)
        self.assertEquals(resp.status_code,200)
    def test_api_new_graph_1_recipe(self):
        """
        Tests the status code the new graph API for type 1 using recipe based models
        """
        department = baker.make_recipe("makeReports.department")
        program = baker.make_recipe("makeReports.degreeProgram",department=department)
        r = baker.make_recipe("makeReports.report", degreeProgram=program, year=2017)
        slo = baker.make_recipe("makeReports.sloInReport",report=r)
        assessHere = baker.make_recipe("makeReports.assessmentVersion",report=r,slo=slo)
        baker.make_recipe("makeReports.assessmentData",assessmentVersion=assessHere,overallProficient=93)
        data = {
            'report__degreeProgram__department': department.pk,
            'report__degreeProgram': program.pk,
            'report__year__gte': 2015,
            'report__year__lte': 2018,
            'decision': 1,
            'sloIR': slo.pk,
            'assess': assessHere.assessment.pk,
            'sloWeights': "{\""+str(slo.pk)+"\": 1}"
        }
        resp = self.client.post(reverse('makeReports:api-new-graph'),data)
        self.assertEquals(resp.status_code,200)
    def test_api_new_graph_2(self):
        """
        Tests the status code the new graph API for type 2
        """
        department = baker.make("Department")
        program = baker.make("DegreeProgram",department=department)
        r = baker.make("Report", degreeProgram=program, year=2018)
        slo = baker.make("SLOInReport",report=r)
        assessHere = baker.make("AssessmentVersion",report=r,slo=slo)
        baker.make("AssessmentData",assessmentVersion=assessHere,overallProficient=93)
        data = {
            'report__degreeProgram__department': department.pk,
            'report__degreeProgram': program.pk,
            'report__year__gte': 2015,
            'report__year__lte': 2018,
            'decision': 2,
            'sloIR': slo.pk,
            'assess': assessHere.assessment.pk,
            'sloWeights': "{\""+str(slo.pk)+"\": 1}"
        }
        resp = self.client.post(reverse('makeReports:api-new-graph'),data)
        self.assertEquals(resp.status_code,200)
    def test_api_new_graph_2_recipe(self):
        """
        Tests the status code the new graph API for type 2 using recipe based models
        """
        department = baker.make_recipe("makeReports.department")
        program = baker.make_recipe("makeReports.degreeProgram",department=department)
        r = baker.make_recipe("makeReports.report", degreeProgram=program, year=2018)
        slo = baker.make_recipe("makeReports.sloInReport",report=r)
        assessHere = baker.make_recipe("makeReports.assessmentVersion",report=r,slo=slo)
        baker.make_recipe("makeReports.assessmentData",assessmentVersion=assessHere,overallProficient=93)
        data = {
            'report__degreeProgram__department': department.pk,
            'report__degreeProgram': program.pk,
            'report__year__gte': 2015,
            'report__year__lte': 2018,
            'decision': 2,
            'sloIR': slo.pk,
            'assess': assessHere.assessment.pk,
            'sloWeights': "{\""+str(slo.pk)+"\": 1}"
        }
        resp = self.client.post(reverse('makeReports:api-new-graph'),data)
        self.assertEquals(resp.status_code,200)
    def test_api_new_graph_3(self):
        """
        Tests the status code the new graph API for type 3
        """
        department = baker.make("Department")
        program = baker.make("DegreeProgram",department=department)
        r = baker.make("Report", degreeProgram=program, year=2016)
        slo = baker.make("SLOInReport",report=r)
        assessHere = baker.make("AssessmentVersion",report=r,slo=slo)
        baker.make("AssessmentData",assessmentVersion=assessHere,overallProficient=93)
        data = {
            'report__degreeProgram__department': department.pk,
            'report__degreeProgram': program.pk,
            'report__year__gte': 2015,
            'report__year__lte': 2018,
            'decision': 3,
            'sloIR': slo.pk,
            'assess': assessHere.assessment.pk,
            'sloWeights': "{\""+str(slo.pk)+"\": 1}"
        }
        resp = self.client.post(reverse('makeReports:api-new-graph'),data)
        self.assertEquals(resp.status_code,200)
    def test_api_new_graph_3_recipe(self):
        """
        Tests the status code the new graph API for type 3 with recipe based models
        """
        department = baker.make_recipe("makeReports.department")
        program = baker.make_recipe("makeReports.degreeProgram",department=department)
        r = baker.make_recipe("makeReports.report", degreeProgram=program, year=2016)
        slo = baker.make_recipe("makeReports.sloInReport",report=r)
        assessHere = baker.make_recipe("makeReports.assessmentVersion",report=r,slo=slo)
        baker.make_recipe("makeReports.assessmentData",assessmentVersion=assessHere,overallProficient=93)
        data = {
            'report__degreeProgram__department': department.pk,
            'report__degreeProgram': program.pk,
            'report__year__gte': 2015,
            'report__year__lte': 2018,
            'decision': 3,
            'sloIR': slo.pk,
            'assess': assessHere.assessment.pk,
            'sloWeights': "{\""+str(slo.pk)+"\": 1}"
        }
        resp = self.client.post(reverse('makeReports:api-new-graph'),data)
        self.assertEquals(resp.status_code,200)
class ActionAPITests(ReportAACSetupTest):
    """
    Tests relating to the action API
    """
    def test_clear_override(self):
        """
        Tests the clear override button clears the overrides
        """
        slo = baker.make("SLOInReport",report=self.rpt)
        aV = baker.make("AssessmentVersion",report=self.rpt,slo=slo)
        aa = baker.make("AssessmentAggregate", override=True,assessmentVersion=aV)
        ss = SLOStatus.objects.get(sloIR=slo)
        ss.override = True
        ss.save()
        self.client.get(reverse('makeReports:api-clear-ovr')+"?pk="+str(self.rpt.pk))
        aa.refresh_from_db()
        ss.refresh_from_db()
        self.assertFalse(aa.override)
        self.assertFalse(ss.override)   



