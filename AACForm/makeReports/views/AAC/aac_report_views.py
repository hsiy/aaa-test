"""
This file contains views directly related to creating, editing, and viewing reports done by the AAC
"""
from datetime import datetime
from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from makeReports.models import DegreeProgram, GradedRubric, GradGoal, Report
from makeReports.forms import CreateReportByDept, CreateReportByDPForm, GradGoalForm, GradGoalEditForm
from makeReports.views.helperFunctions.mixins import AACOnlyMixin


class CreateReport(AACOnlyMixin,CreateView):
    """
    View to create report by department

    Keyword Args:
        dept (str): primary key of :class:`~makeReports.models.aac_models.Department` to create report for
    """
    model = Report
    form_class = CreateReportByDept
    template_name = "makeReports/AACAdmin/manualReportCreate.html"
    #success_url = reverse_lazy('makeReports:admin-home')
    def get_form_kwargs(self):
        """
        Returns the keyword arguments for the form, appending the :class:`~makeReports.models.aac_models.Department` primary key

        Returns:
            dict : form keyword arguments
        """
        kwargs = super(CreateReport, self).get_form_kwargs()
        kwargs['dept'] = self.kwargs['dept']
        return kwargs
    def get_success_url(self):
        """
        Uses success url as hook to set the graded rubric of the report, 
        also returns administrative home as success URL

        Notes:
            The graded rubric was created during form_valid
        Returns:
            str : success url of the administrative home (:class:`~makeReports.views.aac_admin_views.AdminHome`)
        """
        self.object.rubric = self.GR
        self.object.save()
        return reverse_lazy('makeReports:dept-list')
    def form_valid(self, form):
        """
        Saves model based upon form, along with setting submitted to false,
        and attaching a new graded rubric based upon the chosen rubric version
        to the instance

        Args:
            form (CreateReportByDept): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        form.instance.submitted = False
        self.GR = GradedRubric.objects.create(rubricVersion=form.cleaned_data['rubric'])
        return super(CreateReport, self).form_valid(form)
class CreateReportByDP(AACOnlyMixin,CreateView):
    """
    View to create report by degree program

    Keyword Args:
        pk (str): primary key of :class:`~makeReports.models.aac_models.DegreeProgram`
    """
    model = Report
    form_class = CreateReportByDPForm
    template_name = "makeReports/AACAdmin/manualReportCreate.html"
    def get_success_url(self):
        """
        Uses success_url as hook to attach graded rubric to object, and also gets the success URL

        Returns:
            str : success url of administrative home (:class:`~makeReports.views.aac_admin_views.AdminHome`)
        """
        self.object.rubric = self.GR
        self.object.save()
        return reverse_lazy('makeReports:admin-home')
    def form_valid(self,form):
        """
        Sets the degree program, sets submitted to False, creates graded rubric based
        upon the chosen rubric version, and creates Report from form
        
        Args:
            form (CreateReportByDPForm): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        try:
            form.instance.degreeProgram = DegreeProgram.objects.get(pk=self.kwargs['dP'])
        except DegreeProgram.DoesNotExist:
            raise Http404("Degree program matching URL does not exist.")
        form.instance.submitted = False
        self.GR = GradedRubric.objects.create(rubricVersion=form.cleaned_data['rubric'])
        return super(CreateReportByDP,self).form_valid(form)
class DeleteReport(AACOnlyMixin,DeleteView):
    """
    View to delete report

    Keyword Args:
        pk (str): primary key of :class:`~makeReports.models.basic_models.Report` to delete
    """
    model = Report
    template_name = "makeReports/AACAdmin/deleteReport.html"
    success_url = reverse_lazy('makeReports:report-list')
class ReportList(AACOnlyMixin,ListView):
    """
    View to list reports of active degree programs from this year
    """
    model = Report
    template_name = "makeReports/AACAdmin/reportList.html"
    def get_queryset(self):
        """
        Gets reports from this year and active degree programs

        Returns:
            QuerySet : reports (:class:`~makeReports.models.basic_models.Report`) from this year
        """
        qs = Report.objects.filter(
            year=int(datetime.now().year), 
            degreeProgram__active=True
            ).order_by('submitted','rubric__complete','year',"degreeProgram__name")
        return qs
class ReportListSearched(AACOnlyMixin,ListView):
    """
    View to list reports meeting search parameters

    Notes:
        Search parameters passed through GET request,
        'year','submitted', 'graded', 'dP' for degree program primary key,
        'dept' for department by primary key, and 'college' by primary key
    """
    model = Report
    template_name = "makeReports/AACAdmin/reportList.html"
    def get_queryset(self):
        """
        Gets filtered QuerySet based upon parameters

        Returns:
            QuerySet : reports (:class:`~makeReports.models.basic_models.Report`) meeting search criteria
        """
        keys = self.request.GET.keys()
        objs = Report.objects.filter(
            degreeProgram__active=True
        ).order_by('submitted','rubric__complete','year','degreeProgram__name')
        if 'year' in keys:
            year = self.request.GET['year']
            if year!= "":
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
        if 'dept' in keys:
            dept = self.request.GET['dept']
            if dept!="":
                objs=objs.filter(degreeProgram__department__name__icontains=dept)
        if 'college' in keys:
            college = self.request.GET['college']
            if college!="":
                objs=objs.filter(degreeProgram__department__college__name__icontains=college)
        return objs
class ManualReportSubmit(AACOnlyMixin,UpdateView):
    """
    View to manually submitting a report, overriding checks
    """
    model = Report
    fields = ['submitted']
    template_name = 'makeReports/AACAdmin/manualSubmit.html'
    success_url = reverse_lazy('makeReports:report-list')
class MakeGradGoal(AACOnlyMixin,CreateView):
    """
    View to create a new graduate-level goal
    """
    form_class = GradGoalForm
    template_name = "makeReports/AACAdmin/GG/addGG.html"
    success_url = reverse_lazy('makeReports:gg-list')
class UpdateGradGoal(AACOnlyMixin,UpdateView):
    """
    View to change the text of a graduate-level goal

    Keyword Args:
        pk (str): primary key of :class:`~makeReports.models.slo_models.GradGoal` to update
    """
    model = GradGoal
    form_class = GradGoalEditForm
    template_name = "makeReports/AACAdmin/GG/updateGG.html"
    success_url = reverse_lazy('makeReports:gg-list')
class ListActiveGradGoals(AACOnlyMixin,ListView):
    """
    View to list all active graduate-level goals
    """
    model = GradGoal
    template_name = "makeReports/AACAdmin/GG/GGlist.html"
    def get_queryset(self):
        """
        Gets only the active grad goals

        Returns:
            QuerySet : :class:`~makeReports.models.slo_models.GradGoal` objects that are active
        """
        return GradGoal.active_objects.all()
class ListInactiveGradGoals(AACOnlyMixin,ListView):
    """
    View to list all inactive graduate-level goals
    """
    model = GradGoal
    template_name = "makeReports/AACAdmin/GG/oldGGlist.html"
    def get_queryset(self):
        """
        Gets inactive grad goals
        
        Returns:
            QuerySet : :class:`~makeReports.models.slo_models.GradGoal` objects that are inactive
        """
        return GradGoal.objects.filter(active=False)