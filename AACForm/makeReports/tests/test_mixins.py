"""
Tests related to testing mixins authenticate users correctly
"""
from django.test import TestCase, RequestFactory
from makeReports.models import Department, User
from model_bakery import baker
from makeReports.views.helperFunctions.mixins import AACOnlyMixin, DeptAACMixin, DeptOnlyMixin
from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied
from django import forms
from makeReports.forms.cleaners import CleanSummer
from django_summernote.widgets import SummernoteWidget


class AACOnlyMixinTest(TestCase):
    """
    Tests only AAC members can access pages with the AAC mixin
    """
    class DummyView(AACOnlyMixin, TemplateView):
        """
        Dummy view to attach mix-in to
        """
        template_name = 'makeReports/help.html'
    def setUp(self):
        """
        Sets up an instance of the dummy view and a user
        """
        super().setUp()
        self.user = User.objects.create_user( 
                username='Megan',
                email='megan@example.com',
                password = 'passywordy',
            )
        self.col = baker.make("College")
        self.dept = Department.objects.create(name="Dept",college=self.col)
        self.user.profile.department = self.dept
        self.user.profile.save()
        self.client.login(username='Megan', password='passywordy')
        self.factory = RequestFactory()

    def test_aac(self):
        """
        Tests the AAC member can access the page
        """
        self.user.profile.aac = True
        self.user.profile.save()
        request = self.factory.get('/dummy')
        request.user =self.user
        resp = self.DummyView.as_view()(request)
        self.assertEquals(resp.status_code,200)
    def test_notaac(self):
        """
        Tests non-AAC members cannot access the page
        """
        self.user.profile.aac = False
        self.user.profile.save()
        request = self.factory.get('/dummy')
        request.user =self.user
        try:
            self.DummyView.as_view()(request)
            self.assertTrue(False)
        except PermissionDenied:
            self.assertTrue(True)
class AACOnlyMixinTestRecipe(AACOnlyMixinTest):
    """
    Tests only AAC members can access pages with AAC Mixin when model are made from recipes
    """
    def setUp(self):
        """
        Sets up the dummy view and a user using the recipes
        """
        super().setUp()
        self.col = baker.make_recipe("makeReports.college")
        self.dept = Department.objects.create(name="Dept",college=self.col)
        self.user.profile.department = self.dept
        self.user.profile.save()
class DeptOnlyMixinTest(TestCase):
    """
    Tests only department members can access pages with the DeptOnly mixin
    """
    class DummyView(DeptOnlyMixin, TemplateView):
        """
        Dummy view to attach mix-in to
        """
        template_name = 'makeReports/help.html'
        def dispatch(self,request,*args,**kwargs):
            dept = Department.objects.get(name="Dept43")
            self.report = baker.make("Report",degreeProgram__department=dept)
            return super().dispatch(request,*args,**kwargs)

    def setUp(self):
        """
        Sets up an instance of the dummy view and a user
        """
        super().setUp()
        self.user = User.objects.create_user( 
                username='Megan',
                email='megan@example.com',
                password = 'passywordy',
            )
        self.col = baker.make("College")
        self.dept = Department.objects.create(name="Dept43",college=self.col)
        self.client.login(username='Megan', password='passywordy')
        self.factory = RequestFactory()

    def test_aac(self):
        """
        Tests the AAC member not in department cannot access the page
        """
        self.user.profile.aac = True
        self.user.profile.department = baker.make("Department")
        self.user.profile.save()
        request = self.factory.get('/dummy')
        request.user = self.user
        try:
            self.DummyView.as_view()(request)
            self.assertTrue(False)
        except PermissionDenied:
            self.assertTrue(True)
    def test_notaac_indept(self):
        """
        Tests non-AAC member in department can access page
        """
        self.user.profile.aac = False
        self.user.profile.department = self.dept
        self.user.profile.save()
        request = self.factory.get('/dummy')
        request.user =self.user
        resp = self.DummyView.as_view()(request)
        self.assertEquals(resp.status_code,200)
    def test_aac_indept(self):
        """
        Tests AAC member in department can access page
        """
        self.user.profile.aac = True
        self.user.profile.department = self.dept
        self.user.profile.save()
        request = self.factory.get('/dummy')
        request.user =self.user
        resp = self.DummyView.as_view()(request)
        self.assertEquals(resp.status_code,200)
class DeptOnlyMixinTestRecipe(DeptOnlyMixinTest):
    """
    Tests the Department only mixin using recipe based models
    """
    def setUp(self):
        super().setUp()
        self.col = baker.make_recipe("makeReports.college")
class DeptAACMixinTests(TestCase):
    """
    Tests the Department or AAC mix-in works correctly
    """
    class DummyView(DeptAACMixin, TemplateView):
        """
        Dummy view to attach mix-in to
        """
        template_name = 'makeReports/help.html'
        def dispatch(self,request,*args,**kwargs):
            dept = Department.objects.get(name="Dept432")
            self.report = baker.make("Report",degreeProgram__department=dept)
            return super().dispatch(request,*args,**kwargs)

    def setUp(self):
        """
        Sets up an instance of the dummy view and a user
        """
        super().setUp()
        self.user = User.objects.create_user( 
                username='Megan',
                email='megan@example.com',
                password = 'passywordy',
            )
        self.col = baker.make("College")
        self.dept = Department.objects.create(name="Dept432",college=self.col)
        self.client.login(username='Megan', password='passywordy')
        self.factory = RequestFactory()
    def test_inaac(self):
        """
        Tests that AAC members can access the page
        """
        self.user.profile.aac = True
        self.user.profile.department = baker.make("Department")
        self.user.profile.save()
        request = self.factory.get('/dummy')
        request.user = self.user
        resp = self.DummyView.as_view()(request)
        self.assertEquals(resp.status_code,200)
    def test_indept(self):
        """
        Test non-AAC member in department can access page
        """
        self.user.profile.aac = False
        self.user.profile.department = self.dept
        self.user.profile.save()
        request = self.factory.get('/dummy')
        request.user =self.user
        resp = self.DummyView.as_view()(request)
        self.assertEquals(resp.status_code,200)
    def test_aac_indept(self):
        """
        Tests AAC member in department can access page
        """
        self.user.profile.aac = True
        self.user.profile.department = self.dept
        self.user.profile.save()
        request = self.factory.get('/dummy')
        request.user =self.user
        resp = self.DummyView.as_view()(request)
        self.assertEquals(resp.status_code,200)
    def test_notdept(self):
        """
        Tests non-AAC person not in department cannot access the page
        """
        self.user.profile.aac = False
        self.user.profile.department = baker.make("Department", name="NotDept")
        self.user.profile.save()
        self.user.refresh_from_db()
        request = self.factory.get('/dummy')
        request.user = self.user
        try:
            self.DummyView.as_view()(request)
            self.assertTrue(False)
        except PermissionDenied:
            self.assertTrue(True)
class DeptAACMixinTestRecipe(DeptAACMixinTests):
    """
    Tests the department or AAC mixin using recipe based models
    """
    def setUp(self):
        """
        Sets up an instance of the dummy view and the user using recipes
        """
        super().setUp()
        self.col = baker.make_recipe("makeReports.college")
class CleanSummerTests(TestCase):
    """
    Tests that the CleanSummer class works as expected
    """
    class DummyForm(CleanSummer,forms.Form):
        """
        DummyForm to test CleanSummer mixin
        """
        text = forms.CharField(widget=SummernoteWidget(),label="")
        summer_max_length=1000
    def test_valid_is_valid(self):
        """
        Tests valid length is accepted as valid
        """
        f = self.DummyForm({
            'text':'xy'*499
        })
        self.assertTrue(f.is_valid())
    def test_invalid_isnt_valid(self):
        """
        Tests that too long of length is not accepted as valid
        """
        f = self.DummyForm({
            'text':'xyz'*499
        })
        self.assertFalse(f.is_valid())
    def test_scripts_arestripped(self):
        """
        Tests that script tags are stripped
        """
        f = self.DummyForm({
            'text': "<script>Bad things happen</script><p>Not bad things didn't happen</p>"
        })
        f.is_valid()
        self.assertNotIn("<script>",f.cleaned_data['text'])
    def test_not_scripts_arent_stripped(self):
        """
        Tests that things not in script tags and okay HTML tags are not stripped
        """
        f = self.DummyForm({
            'text':"<script></script><p><b>Bad</b><i>things</i>didn't happned</p>"
        })
        f.is_valid()
        self.assertIn("<p><b>Bad</b><i>things</i>didn't happned</p>",f.cleaned_data['text'])

    