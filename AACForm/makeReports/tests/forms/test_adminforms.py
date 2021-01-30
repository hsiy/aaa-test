"""
This tests that the AAC admin forms work
"""
from django.test import TestCase
from model_bakery import baker
from makeReports.forms import (
    AnnouncementForm,
    CreateDepartmentForm, 
    CreateReportByDept,
    CreateReportByDPForm,
    GenerateReports, 
    GradGoalEditForm,
    GradGoalForm,
    MakeNewAccount, 
    UpdateUserForm, 
    UserUpdateUserForm
)
from datetime import datetime

class UserFormsTest(TestCase):
    """
    Tests the user forms work as expected
    """
    def test_update_valid_data(self):
        """
        Tests valid data is valid with the UpdateUserForm
        """
        d = baker.make("Department")
        f = UpdateUserForm({
            'aac':False,
            'department': d.pk,
            'first_name':'Ruby',
            'last_name':"Drake",
            'email':'rdrake@gma.com'
        })
        self.assertTrue(f.is_valid())
    def test_update_valid_data_no_dep(self):
        """
        Tests the UpdateUserForm accepts no department
        """
        baker.make("Department")
        f = UpdateUserForm({
            'aac':True,
            'first_name':'Ruby-Jane',
            'last_name':"Drake",
            'email':'rdrake@gma.com'
        })
        self.assertTrue(f.is_valid())
    def test_update_noname_invalid(self):
        """
        Tests UpdateUserForm requires the first name
        """
        d = baker.make("Department")
        f = UpdateUserForm({
            'aac':False,
            'department':d.pk,
            'last_name':"Drake",
            'email':'drake@gma.com'
        })
        self.assertFalse(f.is_valid())
    def test_users_own_form(self):
        """
        Tests that the UserUpdateUserForm accepts valid data
        """
        f = UserUpdateUserForm({
            'first_name':"Johnny",
            'last_name':"Bertesen",
            "email":'jBet@aac.om'
        })
        self.assertTrue(f.is_valid())
    def test_users_own_form_requires_email(self):
        """
        Tests the the UserUpdateUserForm rejects forms without an email
        """
        f = UserUpdateUserForm({
            'first_name':"Johnny",
            'last_name':"Bertesen",
        })
        self.assertFalse(f.is_valid())
    def test_make_account(self):
        """
        Tests the MakeNewAccount form accepts valid data
        """
        d = baker.make("Department")
        f = MakeNewAccount({
            'isaac': False,
            'department':d.pk,
            'college':d.college.pk,
            'email':'kfldsj@klfjc.com',
            'username':'jliver',
            'password1':'pwpwpwpw',
            'password2':'pwpwpwpw',
            'first_name':"Janey",
            "last_name":"Liverman"
        })
        self.assertTrue(f.is_valid())
    def test_make_account_password_doesnt_match(self):
        """
        Tests the MakeNewAccount form fails when the passwords don't match
        """
        d = baker.make("Department")
        f = MakeNewAccount({
            'isaac': False,
            'department':d.pk,
            'college':d.college.pk,
            'email':'jOmaha@klfjc.com',
            'username':'jOmaha',
            'password1':'pwpwpwpw',
            'password2':'pwp33wpwpw',
            'first_name':"Johnathan",
            "last_name":"Omaha"
        })
        self.assertFalse(f.is_valid())
class DepartmentFormTest(TestCase):
    """
    Tests relating to managing department forms
    """
    def test_create_valid(self):
        """
        Tests the CreateDepartmentForm accepts valid data
        """
        c = baker.make("College",active=True)
        f = CreateDepartmentForm({
            'name':'Psychology',
            'college': c.pk
        })
        self.assertTrue(f.is_valid())
    def test_create_inactive_college(self):
        """
        Tests the CreateDepartmentForms rejects invalid data where the college is inactive
        """
        c = baker.make("College",active=False)
        f = CreateDepartmentForm({
            'name':'College of Education',
            'college':c
        })
        self.assertFalse(f.is_valid())
class GenerateReportsTests(TestCase):
    """
    Tests forms related to generating reports
    """
    def test_valid_data(self):
        """
        Tests the form accepts valid data
        """
        rubric = baker.make("Rubric")
        f = GenerateReports({
            'year':2019,
            'rubric': rubric.pk
        })
        self.assertTrue(f.is_valid())
    def test_invalid_data_no_rub(self):
        """
        Tests the form rejects form missing rubric
        """
        f = GenerateReports({})
        self.assertFalse(f.is_valid())
    def test_invalid_notPK(self):
        """
        Tests the form rejects a form where rubric is not an integer
        """
        f = GenerateReports({
            'year':2019,
            "rubric":"not an int"
        })
        self.assertFalse(f.is_valid())
class AnnouncementFormTest(TestCase):
    """
    Test forms relating to announcements
    """
    def test_valid_data(self):
        """
        Tests the AnnouncementForm accepts valid data
        """
        f = AnnouncementForm({
            'text':"x "*1000,
            'expiration':datetime.now()
        })
        self.assertTrue(f.is_valid())
    def test_toolong(self):
        """
        Tests that announcements that are too long are rejected
        """
        f = AnnouncementForm({
            'text':"xy"*1001,
            'expiration':datetime.now()
        })
        self.assertFalse(f.is_valid())
class GradGoalFormTests(TestCase):
    """
    Tests GradGoal related forms
    """
    def test_goal_valid(self):
        """
        Tests that the GradGoalForm accepts valid data
        """
        f = GradGoalForm({
            'text':'xyz'*100
        })
        self.assertTrue(f.is_valid())
    def test_goal_toolong(self):
        """
        Tests that the GradGoalForm rejects invalid, too long data
        """
        f = GradGoalForm({
            'text':'x'*601
        })
        self.assertFalse(f.is_valid())
    def test_edit_valid(self):
        """
        Tests the GradGoalEditForm accepts valid data
        """
        f = GradGoalEditForm({
            'text':"Students will comprehend detailed instructions.",
            'active': True
        })
        self.assertTrue(f.is_valid())

class ReportFormTests(TestCase):
    """
    Tests forms related to the report management
    """
    def test_create_valid(self):
        """
        Tests CreateReportByDept correctly accepts valid data
        """
        dp = baker.make("DegreeProgram")
        rub = baker.make("Rubric")
        f = CreateReportByDept({
            'year':2017,
            'degreeProgram':dp.pk,
            'rubric': rub.pk
        },dept=dp.department.pk
        )
        self.assertTrue(f.is_valid())
    def test_create_by_DP_valid(self):
        """
        Tests that CreateReportByDPForm accepts valid data
        """
        r = baker.make("Rubric")
        f = CreateReportByDPForm({
            'year':2017,
            'rubric':r.pk
        })
        self.assertTrue(f.is_valid())
    def test_create_by_DP_norubric(self):
        """
        Tests that the CreateReportByDPForm requires the rubric field
        """
        baker.make("Rubric")
        f = CreateReportByDPForm({
            'year':2019
        })
        self.assertFalse(f.is_valid())