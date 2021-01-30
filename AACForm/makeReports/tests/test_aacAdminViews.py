"""
Tests relating to the AAC administration of the website views
"""
from django.urls import reverse
from makeReports.models import Announcement, College, DegreeProgram, Department, GradGoal,Profile, Report
from model_bakery import baker
from .test_basicViews import ReportAACSetupTest
from datetime import datetime, date, timedelta

class AACBasicViewsTest(ReportAACSetupTest):
    """
    Tests the basic AAC admin views, such as home
    """
    def test_home(self):
        """
        Tests the home page exists
        """
        response = self.client.get(reverse('makeReports:admin-home'))
        self.assertEquals(response.status_code,200)
class AACCollegeViewsTest(ReportAACSetupTest):
    """
    Tests the AAC admin views related to the colleges
    """
    def test_create(self):
        """
        Tests that the create college page exists and works
        """
        data = {
            'name': 'College of Arts and Sciences'
        }
        self.client.post(reverse('makeReports:add-college'),data)
        num = College.active_objects.filter(name='College of Arts and Sciences').count()
        self.assertGreaterEqual(num,1)
    def test_list(self):
        """
        Tests the list page contains a college made and not an inactive college
        """
        col = baker.make("College", active=True)
        colI = baker.make("College",active=False)
        response = self.client.get(reverse('makeReports:college-list'))
        self.assertContains(response,col.name)
        self.assertNotContains(response,colI.name)
    def test_list_recipe(self):
        """
        Tests the list page contains a college made and not an inactive college using recipe based colleges
        """
        col = baker.make_recipe("makeReports.college", active=True)
        colI = baker.make_recipe("makeReports.college",active=False)
        response = self.client.get(reverse('makeReports:college-list'))
        self.assertContains(response,col.name)
        self.assertNotContains(response,colI.name)
    def test_delete(self):
        """
        Tests the delete page deletes the college
        """
        col = baker.make("College")
        pk = col.pk
        self.client.post(reverse('makeReports:delete-college',kwargs={'pk':col.pk}))
        num = College.active_objects.filter(pk=pk).count()
        self.assertEquals(num,0)
    def test_delete_DNE(self):
        """
        Tests 404 when college does not exist to delete
        """
        response = self.client.post(reverse('makeReports:delete-college',kwargs={'pk':89}))
        self.assertEquals(response.status_code,404)
    def test_delete_recipe(self):
        """
        Tests the delete page deletes the college using recipe based model
        """
        col = baker.make_recipe("makeReports.college")
        pk = col.pk
        self.client.post(reverse('makeReports:delete-college',kwargs={'pk':col.pk}))
        num = College.active_objects.filter(pk=pk).count()
        self.assertEquals(num,0)
    def test_recover(self):
        """
        Tests the recover page in fact re-marks the college as active
        """
        col = baker.make("College",active=False)
        r = self.client.get(reverse('makeReports:recover-college',kwargs={'pk':col.pk}))
        self.assertEquals(r.status_code,200)
        self.client.post(reverse('makeReports:recover-college',kwargs={'pk':col.pk}),{'active':'on'})
        col.refresh_from_db()
        self.assertTrue(col.active)
    def test_recover_DNE(self):
        """
        Tests the recover page returns 404 when it does not exist
        """
        r = self.client.get(reverse('makeReports:recover-college',kwargs={'pk':101}))
        self.assertEquals(r.status_code,404)
    def test_recover_recipe(self):
        """
        Tests the recover page in fact re-marks the college as active using recipe based model
        """
        col = baker.make_recipe("makeReports.college",active=False)
        self.client.post(reverse('makeReports:recover-college',kwargs={'pk':col.pk}),{'active':'on'})
        col.refresh_from_db()
        self.assertTrue(col.active)
    def test_arc_cols(self):
        """
        Tests that the archived college page contains only archived colleges
        """
        c1 = baker.make("College",active=True)
        c2 = baker.make("College",active=False)
        r = self.client.get(reverse('makeReports:arc-colleges'))
        self.assertNotContains(r,c1.name)
        self.assertContains(r,c2.name)
    def test_arc_cols_recipe(self):
        """
        Tests that the archived college page contains only archived colleges using recipe based model
        """
        c1 = baker.make_recipe("makeReports.college",active=True)
        c2 = baker.make_recipe("makeReports.college",active=False)
        r = self.client.get(reverse('makeReports:arc-colleges'))
        self.assertNotContains(r,c1.name)
        self.assertContains(r,c2.name)
class DepartmentViewsTest(ReportAACSetupTest):
    """
    Tests the views relating to department administration
    """
    def test_create(self):
        """
        Tests that posting to the create department page works as expected
        """
        col = baker.make("College")
        data = {
            'name':'History',
            'college': col.pk
        }
        self.client.post(reverse('makeReports:add-dept'),data)
        num = Department.objects.filter(name='History',college=col).count()
        self.assertGreaterEqual(num,1)
    def test_list(self):
        """
        Tests that list of department contains active departments
        """
        dept = baker.make("Department")
        dep2 = baker.make("Department",active=False)
        response = self.client.get(reverse('makeReports:dept-list')+"?college=&name=")
        self.assertContains(response,dept.name)
        self.assertNotContains(response,dep2.name)
    def test_update(self):
        """
        Tests that updating department works as expected
        """
        dept = baker.make("Department")
        r = self.client.get(reverse('makeReports:update-dept',kwargs={'pk':dept.pk}))
        self.assertEquals(r.status_code, 200)
        r = self.client.post(reverse('makeReports:update-dept',kwargs={'pk':dept.pk}),{'name':"d name 2","college":dept.college.pk})
        dept.refresh_from_db()
        self.assertEquals(dept.name,"d name 2")
    def test_update_DNE(self):
        """
        Tests the update page returns 404 when it does not exist
        """
        r = self.client.get(reverse('makeReports:update-dept',kwargs={'pk':103}))
        self.assertEquals(r.status_code,404)
    def test_delete(self):
        """
        Tests that the delete view marks the department inactive
        """
        dept = baker.make("Department",active=True)
        r = self.client.get(reverse('makeReports:delete-dept',kwargs={'pk':dept.pk}))
        self.assertEquals(r.status_code,200)
        r = self.client.post(reverse('makeReports:delete-dept',kwargs={'pk':dept.pk}))
        dept.refresh_from_db()
        self.assertFalse(dept.active)
    def test_delete_DNE(self):
        """
        Tests the delete page returns 404 when the object does not exist
        """
        r = self.client.get(reverse('makeReports:delete-dept',kwargs={'pk':103}))
        self.assertEquals(r.status_code,404)
    def test_recover(self):
        """
        Tests that recovering a department works as expected
        """
        dept = baker.make("Department",active=False)
        r = self.client.get(reverse('makeReports:recover-dept',kwargs={'pk':dept.pk}))
        self.assertEquals(r.status_code,200)
        r = self.client.post(reverse('makeReports:recover-dept',kwargs={'pk':dept.pk}),{'active':'on'})
        dept.refresh_from_db()
        self.assertTrue(dept.active)
    def test_recover_DNE(self):
        """
        Tests the recover department page returns 404 when the object does not exist
        """
        r = self.client.get(reverse('makeReports:recover-dept',kwargs={'pk':922}))
        self.assertEquals(r.status_code,404)
    def test_arc_depts(self):
        """
        Tests that the archived department lists contains only inactive departments
        """
        d1 = baker.make("Department",active=True)
        d2 = baker.make("Department",active=False)
        r = self.client.get(reverse('makeReports:arc-depts'))
        self.assertContains(r,d2.name)
        self.assertNotContains(r,d1.name)
class DegreeProgramAdminTest(ReportAACSetupTest):
    """
    Tests that views relating degree program administration
    """
    def setUp(self):
        super(DegreeProgramAdminTest,self).setUp()
        self.dept = baker.make("Department")
    def test_create(self):
        """
        Tests that a degree program is created
        """
        r = self.client.get(reverse('makeReports:add-dp',kwargs={'dept':self.dept.pk}))
        self.assertEquals(r.status_code,200)
        r = self.client.post(reverse('makeReports:add-dp',kwargs={'dept':self.dept.pk}),{
            'name':'Poetry',
            'level':"UG",
            'cycle': 5,
            'startingYear': 7
        })
        num = DegreeProgram.objects.filter(department=self.dept,name='Poetry',cycle=5, startingYear=7, level="UG").count()
        self.assertGreaterEqual(num, 1)
    def test_create_emptyslots(self):
        """
        Tests that a degree program is created when cycle and starting year are left blank
        """
        self.client.post(reverse('makeReports:add-dp',kwargs={'dept':self.dept.pk}),{
            'name':'Secondary education',
            'level':'GR',
            'cycle': 0
        })
        num = DegreeProgram.objects.filter(department=self.dept,name='Secondary education', level="GR").count()
        self.assertGreaterEqual(num, 1)
    def test_update(self):
        """
        Tests that a degree program is effectively updated
        """
        dp = baker.make("DegreeProgram",department=self.dept)
        r = self.client.get(reverse('makeReports:update-dp',kwargs={'dept':self.dept.pk,'pk':dp.pk}))
        self.assertEquals(r.status_code,200)
        r = self.client.post(reverse('makeReports:update-dp',kwargs={'dept':self.dept.pk,'pk':dp.pk}),{
            'name':'History',
            'level':'GR',
        })
        dp.refresh_from_db()
        self.assertEquals(dp.name,'History')
        self.assertEquals(dp.level,'GR')
    def test_update_DNE(self):
        """
        Tests the update DP page returns 404 when the object does not exist
        """
        r = self.client.get(reverse('makeReports:update-dp',kwargs={'dept':self.dept.pk,'pk':910}))
        self.assertEquals(r.status_code,404)
    def test_recover(self):
        """
        Tests that recovering a DP works and sets it to active
        """
        dp = baker.make("DegreeProgram",active=False,department=self.dept)
        rep = self.client.get(reverse('makeReports:recover-dp',kwargs={'dept':self.dept.pk,'pk':dp.pk}),{'active':'on'})
        self.assertEquals(rep.status_code,200)
        self.client.post(reverse('makeReports:recover-dp',kwargs={'dept':self.dept.pk,'pk':dp.pk}),{'active':'on'})
        dp.refresh_from_db()
        self.assertTrue(dp.active)
    def test_delete(self):
        """
        Tests that deleting a DP sets it to inactive
        """
        dp = baker.make("DegreeProgram",active=True,department=self.dept)
        r = self.client.get(reverse('makeReports:delete-dp',kwargs={'dept':self.dept.pk,'pk':dp.pk}))
        self.assertEquals(r.status_code,200)
        self.client.post(reverse('makeReports:delete-dp',kwargs={'dept':self.dept.pk,'pk':dp.pk}))
        dp.refresh_from_db()
        self.assertFalse(dp.active)
    def test_delete_DNE(self):
        """
        Tests the delete DP page returns 404 when the object does not exist
        """
        r = self.client.get(reverse('makeReports:delete-dp',kwargs={'dept':self.dept.pk,'pk':510}))
        self.assertEquals(r.status_code,404)
    def test_arc_dps(self):
        """
        Tests that the archived degree program page contains only archived programs
        """
        dept = baker.make("Department")
        dept2 = baker.make("Department")
        dp = baker.make("DegreeProgram",active=True,department=dept)
        dp2 = baker.make("DegreeProgram",active=False,department=dept)
        dp3 = baker.make("DegreeProgram",active=False,department=dept2)
        r = self.client.get(reverse('makeReports:arc-dps',kwargs={'dept':dept.pk}))
        self.assertContains(r,dp2.name)
        self.assertNotContains(r,dp.name)
        self.assertNotContains(r,dp3.name)
    def test_arc_DNE(self):
        """
        Tests the archived DP page returns 404 when the object does not exist
        """
        r = self.client.get(reverse('makeReports:arc-dps',kwargs={'dept':9291}))
        self.assertEquals(r.status_code,404)
class DegreeProgramAdminTestRecipe(DegreeProgramAdminTest):
    """
    Tests views relating to degree program administration with recipe based models
    """
    def setUp(self):
        """
        Sets up the department from a recipe
        """
        super().setUp()
        self.dept = baker.make_recipe("makeReports.department")
    def test_update(self):
        """
        Tests the update page using a recipe
        """
        dp = baker.make_recipe("makeReports.degreeProgram",department=self.dept)
        r = self.client.get(reverse('makeReports:update-dp',kwargs={'dept':self.dept.pk,'pk':dp.pk}))
        self.assertEquals(r.status_code,200)
        r = self.client.post(reverse('makeReports:update-dp',kwargs={'dept':self.dept.pk,'pk':dp.pk}),{
            'name':'Accounting',
            'level':'GR',
        })
        dp.refresh_from_db()
        self.assertEquals(dp.name,'Accounting')
        self.assertEquals(dp.level,'GR')
    def test_update_DNE(self):
        """
        Tests the update DP page returns 404 when the object does not exist
        """
        r = self.client.get(reverse('makeReports:update-dp',kwargs={'dept':self.dept.pk,'pk':901}))
        self.assertEquals(r.status_code,404)
    def test_delete(self):
        """
        Tests the delete page using recipe based degree program
        """
        dp = baker.make_recipe("makeReports.degreeProgram",active=True,department=self.dept)
        r = self.client.get(reverse('makeReports:delete-dp',kwargs={'dept':self.dept.pk,'pk':dp.pk}))
        self.assertEquals(r.status_code,200)
        self.client.post(reverse('makeReports:delete-dp',kwargs={'dept':self.dept.pk,'pk':dp.pk}))
        dp.refresh_from_db()
        self.assertFalse(dp.active)
    def test_delete_DNE(self):
        """
        Tests the delete DP page returns 404 when the object does not exist
        """
        r = self.client.get(reverse('makeReports:delete-dp',kwargs={'dept':self.dept.pk,'pk':839}))
        self.assertEquals(r.status_code,404)

class ReportAdminViewTests(ReportAACSetupTest):
    """
    Tests views relating to administrating reports
    """
    def test_create_by_dp(self):
        """
        Tests that creating a report by DP works
        """
        dp = baker.make("DegreeProgram")
        rub = baker.make("Rubric")
        r = self.client.get(reverse('makeReports:add-rpt-dp',kwargs={'dP':dp.pk}))
        self.assertEquals(r.status_code,200)
        self.client.post(reverse('makeReports:add-rpt-dp',kwargs={'dP':dp.pk}),{'year':2018,'rubric':rub.pk})
        num = Report.objects.filter(year=2018,degreeProgram=dp).count()
        self.assertEquals(num, 1)
    def test_delete(self):
        """
        Tests that reports get deleted
        """
        pk = self.rpt.pk
        r=self.client.get(reverse('makeReports:delete-rpt',kwargs={'pk':self.rpt.pk}))
        self.assertEquals(r.status_code,200)
        self.client.post(reverse('makeReports:delete-rpt',kwargs={'pk':self.rpt.pk}))
        num = Report.objects.filter(pk=pk).count()
        self.assertEquals(num,0)
    def test_submit(self):
        """
        Tests that the AAC can manually submit reports
        """
        rep = baker.make("Report",submitted=False)
        r = self.client.get(reverse('makeReports:manual-submit-rpt',kwargs={'pk':rep.pk}))
        self.assertEquals(r.status_code,200)
        self.client.post(reverse('makeReports:manual-submit-rpt',kwargs={'pk':rep.pk}),{'submitted':'on'})
        rep.refresh_from_db()
        self.assertTrue(rep.submitted)
    def test_list(self):
        """
        Tests that the report lists reports
        """
        r = baker.make("Report",rubric__complete=False, year=int(datetime.now().year),degreeProgram__active=True)
        response= self.client.get(reverse('makeReports:report-list'))
        self.assertContains(response,r.degreeProgram.name)
        self.assertContains(response,r.year)
    def test_search(self):
        """
        Tests the search functionality
        """
        baker.make("Report",submitted=False, year=2118)
        r2 = baker.make("Report",submitted = True, year=2120)
        response = self.client.get(reverse('makeReports:search-reports')+"?year=2120&submitted=1&dP=&dept=&college=&graded=")
        self.assertContains(response,r2.degreeProgram.name)
        self.assertNotContains(response,2118)
        self.assertContains(response,2120)
    def test_success(self):
        """
        Ensures that the rubric success page exists
        """
        r = self.client.get(reverse('makeReports:gen-rpt-suc'))
        self.assertEquals(r.status_code,200)
class AccountAdminTests(ReportAACSetupTest):
    """
    Tests views relating to account administration
    """
    def test_create(self):
        """
        Tests the creation of new accounts
        """
        dept = baker.make("Department")
        r = self.client.get(reverse('makeReports:make-account'))
        self.assertEquals(r.status_code,200)
        r = self.client.post(reverse('makeReports:make-account'),{
            'isaac':'on',
            'department':dept.pk,
            'college':dept.college.pk,
            'email':'sJames@ksld.com',
            'username':'sJames2',
            'password1':'pwpwpwpw',
            'password2':'pwpwpwpw',
            'first_name':'Sonya-Joe',
            'last_name':'James-Michael'
            })
        num = Profile.objects.filter(aac=True,department=dept,user__first_name='Sonya-Joe').count()
        self.assertEquals(num,1)
    def test_list(self):
        """
        Tests the account list
        """
        a = baker.make("User")
        r = self.client.get(reverse('makeReports:account-list'))
        self.assertContains(r,a.first_name)
    def test_list_search(self):
        """
        Tests the acount list acts as expected
        """
        a = baker.make("User",first_name="Janet")
        baker.make("User",first_name="Tucker")
        r = self.client.get(reverse('makeReports:search-account-list')+"?f="+a.first_name+"&l="+a.last_name+"&e=")
        self.assertContains(r,a.first_name)
        self.assertNotContains(r,"Tucker")
    def test_modify(self):
        """
        Tests the AAC modifying user account page
        """
        a = baker.make("User")
        a.profile.aac = False
        a.profile.save()
        dept = baker.make("Department")
        r = self.client.get(reverse('makeReports:aac-modify-account',kwargs={'pk':a.pk}))
        self.assertEquals(r.status_code,200)
        fD = {
            'aac':'on',
            'department':dept.pk,
            'first_name':'Tina',
            'last_name':'Fey',
            'email':'tfey@g.com'
        }
        r = self.client.post(reverse('makeReports:aac-modify-account',kwargs={'pk':a.pk}),fD)
        a.refresh_from_db()
        self.assertEquals(a.profile.aac,True)
        self.assertEquals(a.profile.department,dept)
        self.assertEquals(a.first_name,'Tina')
        self.assertEquals(a.last_name,'Fey')
        self.assertEquals(a.email,'tfey@g.com')
    def test_inactivate(self):
        """
        Tests the inactivate user view
        """
        a = baker.make("User", is_active=True)
        r = self.client.get(reverse('makeReports:inactivate-account',kwargs={'pk':a.pk}))
        self.assertEquals(r.status_code,200)
        r = self.client.post(reverse('makeReports:inactivate-account',kwargs={'pk':a.pk}))
        a.refresh_from_db()
        self.assertEquals(a.is_active,False)
class GradGoalAdminTests(ReportAACSetupTest):
    """
    Tests views relating to graduate goal administration by the AAC
    """
    def test_list(self):
        """
        Tests the graduate goal list page contains grad goals
        """
        r1 = baker.make("GradGoal",active=True)
        r2 = baker.make("GradGoal",active=False)
        r = self.client.get(reverse('makeReports:gg-list'))
        self.assertContains(r,r1.text)
        self.assertNotContains(r,r2.text)
    def test_list_recipe(self):
        """
        Tests the graduate goal list page contains grad goals using recipe based model
        """
        r1 = baker.make_recipe("makeReports.gradGoal",active=True)
        r2 = baker.make_recipe("makeReports.gradGoal",active=False)
        r = self.client.get(reverse('makeReports:gg-list'))
        self.assertContains(r,r1.text)
        self.assertNotContains(r,r2.text)
    def test_old_list(self):
        """
        Tests the archived list contains expected goals
        """
        r1 = baker.make("GradGoal",active=True)
        r2 = baker.make("GradGoal",active=False)
        r = self.client.get(reverse('makeReports:old-gg-list'))
        self.assertContains(r,r2.text)
        self.assertNotContains(r,r1.text)
    def test_old_list_recipe(self):
        """
        Tests the archived list contains expected goals using recipe based grad goals
        """
        r1 = baker.make_recipe("makeReports.gradGoal",active=True)
        r2 = baker.make_recipe("makeReports.gradGoal",active=False)
        r = self.client.get(reverse('makeReports:old-gg-list'))
        self.assertContains(r,r2.text)
        self.assertNotContains(r,r1.text)
    def test_update(self):
        """
        Tests the update function of the graduate goal
        """
        r = baker.make("GradGoal",active=False)
        resp = self.client.get(reverse('makeReports:update-gg',kwargs={'pk':r.pk}))
        self.assertEquals(resp.status_code,200)
        self.client.post(reverse('makeReports:update-gg',kwargs={'pk':r.pk}),{
            'active':'on',
            'text':'Students will perform community service.'
        })
        r.refresh_from_db()
        self.assertEquals(r.active,True)
        self.assertEquals(r.text,'Students will perform community service.')
    def test_update_recipe(self):
        """
        Tests the update function of the graduate goal with recipe based model
        """
        r = baker.make_recipe("makeReports.gradGoal",active=False)
        self.client.post(reverse('makeReports:update-gg',kwargs={'pk':r.pk}),{
            'active':'on',
            'text':'Students will create original content.'
        })
        r.refresh_from_db()
        self.assertEquals(r.active,True)
        self.assertEquals(r.text,'Students will create original content.')
    def test_add(self):
        """
        Tests that a new graduate goal can be effectively added
        """
        r = self.client.get(reverse('makeReports:add-gg'))
        self.assertEquals(r.status_code,200)
        r = self.client.post(reverse('makeReports:add-gg'),{
            'text':'Students will synthesis information and communicate.'
        })
        num = GradGoal.objects.filter(text='Students will synthesis information and communicate.', active=True).count()
        self.assertEquals(num,1)
class AnnouncementsTest(ReportAACSetupTest):
    """
    Tests that announcements can be appropriately created
    """
    def test_add(self):
        """
        Tests adding an announcement
        """
        r = self.client.get(reverse('makeReports:add-announ'))
        self.assertEquals(r.status_code,200)
        r = self.client.post(reverse('makeReports:add-announ'),{
            'text':'All reports must be submitted this week.',
            'expiration_month':2,
            'expiration_day': 17,
            'expiration_year':2020
        })
        num = Announcement.objects.filter(text='All reports must be submitted this week.',expiration=date(2020,2,17)).count()
        self.assertEquals(num,1)
    def test_list(self):
        """
        Tests the announcement listing page
        """
        an = baker.make("Announcement", expiration=datetime.now()+timedelta(days=1))
        an2 = baker.make("Announcement",expiration=datetime.now()-timedelta(days=2))
        r = self.client.get(reverse('makeReports:announ-list'))
        self.assertContains(r,an.text)
        self.assertContains(r,an2.text)
    def test_list_recipe(self):
        """
        Tests the announcement listing page with recipe based models
        """
        an = baker.make_recipe("makeReports.announcement", expiration=datetime.now()+timedelta(days=1))
        an2 = baker.make_recipe("makeReports.announcement",expiration=datetime.now()-timedelta(days=2))
        r = self.client.get(reverse('makeReports:announ-list'))
        self.assertContains(r,an.text)
        self.assertNotContains(r,an2.text)    
    def test_delete(self):
        """
        Tests that announcements can be effectively deleted
        """
        a = baker.make("Announcement")
        pk = a.pk
        r = self.client.get(reverse('makeReports:delete-announ',kwargs={'pk':a.pk}))
        self.assertEquals(r.status_code,200)
        r = self.client.post(reverse('makeReports:delete-announ',kwargs={'pk':a.pk}))
        num = Announcement.objects.filter(pk=pk).count()
        self.assertEquals(num,0)
    def test_delete_DNE(self):
        """
        Tests the delete announcement page returns 404 when the object does not exist
        """
        r = self.client.get(reverse('makeReports:delete-announ',kwargs={'pk':929}))
        self.assertEquals(r.status_code,404)
    def test_delete_recipe(self):
        """
        Tests that announcements can be effectively deleted with recipe based models
        """
        a = baker.make_recipe("makeReports.announcement")
        pk = a.pk
        self.client.post(reverse('makeReports:delete-announ',kwargs={'pk':a.pk}))
        num = Announcement.objects.filter(pk=pk).count()
        self.assertEquals(num,0)
    def test_edit(self):
        """
        Tests that the edit page effectively edits announcements
        """
        a = baker.make("Announcement")
        r = self.client.get(reverse('makeReports:edit-announ',kwargs={'pk':a.pk}))
        self.assertEquals(r.status_code,200)
        r = self.client.post(reverse('makeReports:edit-announ',kwargs={'pk':a.pk}),{
            'text':'There are some technical difficulties. Please be paitent.',
            'expiration_month':3,
            'expiration_day': 27,
            'expiration_year':2021
        })
        a.refresh_from_db()
        self.assertEquals(a.text,'There are some technical difficulties. Please be paitent.')
        self.assertEquals(a.expiration, date(2021,3,27))
        self.assertEquals(r.status_code,302)
    def test_edit_DNE(self):
        """
        Tests the edit announcement page returns 404 when the object does not exist
        """
        r = self.client.get(reverse('makeReports:edit-announ',kwargs={'pk':929}))
        self.assertEquals(r.status_code,404)
    def test_edit_notday(self):
        """
        Tests the edit page fails when the date is not a valid day
        """
        a = baker.make("Announcement")
        r = self.client.post(reverse('makeReports:edit-announ',kwargs={'pk':a.pk}),{
            'text':'There are some technical difficulties. Please be paitent.',
            'expiration_month':3,
            'expiration_day': 272,
            'expiration_year':2021
        })
        self.assertNotEquals(r.status_code,302)
    def test_edit_missingyear(self):
        """
        Tests the edit page fails when the posted data is missing the year
        """
        a = baker.make_recipe("makeReports.announcement")
        r = self.client.post(reverse('makeReports:edit-announ',kwargs={'pk':a.pk}),{
            'text':'There are some technical difficulties. Please be paitent.',
            'expiration_month':3,
            'expiration_day': 27,
        })
        self.assertNotEquals(r.status_code,302)
    def test_edit_recipe(self):
        """
        Tests that the edit page effectively edits announcements using recipe based announcement
        """
        a = baker.make_recipe("makeReports.announcement")
        self.client.post(reverse('makeReports:edit-announ',kwargs={'pk':a.pk}),{
            'text':'There are some technical difficulties. Please be paitent and kind.',
            'expiration_month':3,
            'expiration_day': 27,
            'expiration_year':2021
        })
        a.refresh_from_db()
        self.assertEquals(a.text,'There are some technical difficulties. Please be paitent and kind.')
        self.assertEquals(a.expiration, date(2021,3,27))
    
    

    

