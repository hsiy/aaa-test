"""
This file contains miscellaneous views that are used by many users
"""
from datetime import datetime
from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from makeReports.models import (
    Announcement,
    Report,
    ReportSupplement
)
from makeReports.forms import UserUpdateUserForm
from makeReports.views.helperFunctions.section_context import (
    section1Context,
    section2Context,
    section3Context,
    section4Context
)
from makeReports.views.helperFunctions.mixins import DeptAACMixin

class HomePage(ListView):
    """
    Home page view
    """
    template_name = "makeReports/home.html"
    model = Report
    def get_queryset(self):
        """
        When logged in, this returns unsubmitted reports within the user's department

        Returns:
            QuerySet : :class:`~makeReports.models.basic_models.Report` objects that need work
        """
        try:
            objs = Report.objects.filter(
                degreeProgram__department=self.request.user.profile.department, 
                submitted=False, 
                degreeProgram__active=True
                ).order_by("degreeProgram__name")
        except:
            objs = None
        return objs
    def get_context_data(self, **kwargs):
        """
        Returns context for template, including the current user, graded reports, and announcements

        Returns:
            dict : template context
        """
        context=super(HomePage,self).get_context_data(**kwargs)
        try:
            context['user']=self.request.user
            context['gReps'] = Report.objects.filter(
                degreeProgram__department=self.request.user.profile.department,
                rubric__complete=True, 
                year=int(datetime.now().year)
                ).order_by("degreeProgram__name")
            context['announ'] = Announcement.objects.filter(
                expiration__gte=datetime.now()
                ).order_by("-creation")
        except:
            pass
        return context
class FacultyReportList(LoginRequiredMixin,ListView):
    """
    View to list all reports within the department
    """
    template_name = "makeReports/reportList.html"
    model = Report
    def get_queryset(self):
        """
        Gets QuerySet of reports within the department
        
        Returns:
            QuerySet : reports (:class:`~makeReports.models.basic_models.Report`) within department 
        """
        objs = Report.objects.filter(
            degreeProgram__department=self.request.user.profile.department, 
            degreeProgram__active=True
            ).order_by("-year",'degreeProgram__name')
        return objs
class ReportListSearchedDept(LoginRequiredMixin,ListView):
    """
    View to search all reports within a department

    Notes:
        Search parameters sent through get request, with 'year', 
        'submitted', 'graded', and 'dP' for primary key of degree program
    """
    model = Report
    template_name = "makeReports/reportList.html"
    def get_queryset(self):
        """
        Gets QuerySet based upon search parameters
        
        Returns:
            QuerySet : reports (:class:`~makeReports.models.basic_models.Report`) within department matching search
        """
        keys = self.request.GET.keys()
        objs = Report.objects.filter(
            degreeProgram__department=self.request.user.profile.department, 
            degreeProgram__active=True
            )
        if 'year' in keys:
            year = self.request.GET['year']
            if year!="":
                objs=objs.filter(year=year)
        if 'submitted' in keys:
            submitted = self.request.GET['submitted']
            if submitted == "S":
                objs=objs.filter(submitted=True)
            elif submitted == "nS":
                objs=objs.filter(submitted=False)
        if 'graded' in keys:
            graded = self.request.GET['graded']
            if graded=="S":
                objs=objs.filter(rubric__complete=True)
            elif graded=="nS":
                objs=objs.filter(rubric__complete=False)
        if 'dP' in keys:
            objs=objs.filter(degreeProgram__name__icontains=self.request.GET['dP'])
        return objs.order_by('submitted','-rubric__complete',"-year","degreeProgram__name")
class DisplayReport(DeptAACMixin,TemplateView):
    """
    View to see report

    Keyword Args:
        pk (str): primary key of :class:`~makeReports.models.basic_models.Report` to display
    """
    template_name = "makeReports/DisplayReport/report.html"
    def dispatch(self,request,*args,**kwargs):
        """
        Dispatches view and attaches :class:`~makeReports.models.basic_models.Report` to instance

        Args:
            request (HttpRequest): request to view page
            
        Keyword Args:
            pk (str): primary key of :class:`~makeReports.models.basic_models.Report` to display
        Returns:
            HttpResponse : response of page to request
        """
        try:
            self.report = Report.objects.get(pk=self.kwargs['pk'])
        except Report.DoesNotExist:
            raise Http404("No report matches the URL.")
        return super(DisplayReport,self).dispatch(request,*args,**kwargs)
    def get_context_data(self, **kwargs):
        """
        Gets template context, including the report, report supplements, and context needed 
        for displaying all 4 sections

        Returns:
            dict : context for template
        """
        context = super(DisplayReport,self).get_context_data(**kwargs)
        context['rpt'] = self.report
        context['reportSups'] = ReportSupplement.objects.filter(report=self.report)
        context = section1Context(self,context)
        context = section2Context(self,context)
        context = section3Context(self,context)
        context = section4Context(self,context)
        return context
class UserModifyAccount(LoginRequiredMixin,FormView):
    """
    View to update a user's own account
    """
    form_class = UserUpdateUserForm
    success_url = reverse_lazy('makeReports:home-page')
    template_name = "makeReports/AACAdmin/modify_account.html"
    def dispatch(self, request,*args,**kwargs):
        """
        Dispatches view and attaches :class:`~django.contrib.auth.models.User` to instance

        Args:
            request (HttpRequest): request to view page
            
        Returns:
            HttpResponse : response of page to request
        """
        self.userToChange = self.request.user
        return super(UserModifyAccount,self).dispatch(request,*args,**kwargs)
    def get_context_data(self, **kwargs):
        context =  super().get_context_data()
        context["first_name"] = self.userToChange.first_name
        context["last_name"] = self.userToChange.last_name
        context["department"] = self.userToChange.profile.department
        context["username"] = self.userToChange.username
        return context
    def get_initial(self):
        """
        Initializes form based upon the current values

        Returns:
            dict : initial form values
        """
        initial = super(UserModifyAccount,self).get_initial()
        try:
            initial['first_name'] = self.userToChange.first_name
            initial['last_name'] = self.userToChange.last_name
            initial['email'] = self.userToChange.email
        except:
            pass
        return initial
    def form_valid(self,form):
        """
        Sets user to attributes given in form

        Args:
            form (UserUpdateUserForm): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        self.userToChange.first_name = form.cleaned_data['first_name']
        self.userToChange.last_name = form.cleaned_data['last_name']
        self.userToChange.email = form.cleaned_data['email']
        self.userToChange.save()
        return super(UserModifyAccount,self).form_valid(form)
class HelpPage(TemplateView):
    """
    View of help page
    """
    template_name = "makeReports/help.html"
