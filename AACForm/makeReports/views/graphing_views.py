"""
This file contains views related to graphing
"""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from makeReports.models import College, AssessmentData
from makeReports.views.helperFunctions.mixins import AACOnlyMixin
from makeReports.views.helperFunctions.csvExport import CSVExportView

class GraphingHome(AACOnlyMixin,TemplateView):
    """
    View of page to generate graphs for the AAC
    """
    template_name = "makeReports/Graphing/graphing.html"
    def get_context_data(self, **kwargs):
        """
        Returns the currently active colleges needed to display the page

        Returns:
            context (dict): dictionary of context including active colleges
        """
        context = super(GraphingHome, self).get_context_data(**kwargs)
        context['colleges'] = College.active_objects.all().order_by("name")
        return context
class GraphingDept(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    View of page for users to create graphs within the department
    """
    template_name = "makeReports/Graphing/graphing_dept.html"
    def test_func(self):
        """
        Ensures user is part of the department for requested page

        Returns:
            bool : whether user is part of the department and can access page
        """
        return self.request.user.profile.department.pk == int(self.kwargs['dept'])
class OutputCSVDepartment(LoginRequiredMixin, UserPassesTestMixin,CSVExportView):
    """
    CSV generating page for within the department

    Keyword Args:
        gYear (str): the minimum year for data
        lYear (str): the maximum year for data
        dept (str): the primary key of the desired department
    """
    model = AssessmentData
    fields = [
        'assessmentVersion__report__year',
        'assessmentVersion__report__degreeProgram', 'assessmentVersion__report__degreeProgram__name',
        'assessmentVersion__report',
        'assessmentVersion__slo', 'assessmentVersion__slo__goalText', 'assessmentVersion__slo__changedFromPrior',
        'assessmentVersion__slo__slo__blooms',
        'assessmentVersion__assessment', 'assessmentVersion__assessment__title',
        'assessmentVersion__assessment__domainExamination', 
        'assessmentVersion__assessment__domainProduct', 
        'assessmentVersion__assessment__domainPerformance',
        'assessmentVersion__assessment__directMeasure',
        'assessmentVersion', 'assessmentVersion__assessmentaggregate__aggregate_proficiency',
        'assessmentVersion__assessmentaggregate__met',
        'assessmentVersion__date', 'assessmentVersion__description',
        'assessmentVersion__finalTerm', 'assessmentVersion__where',
        'assessmentVersion__allStudents', 'assessmentVersion__sampleDescription',
        'assessmentVersion__frequencyChoice', 'assessmentVersion__frequency',
        'assessmentVersion__threshold', 'assessmentVersion__target', 'assessmentVersion__changedFromPrior',
        'dataRange','numberStudents','overallProficient',
        ]
    def get_field_value(self,obj, field_name):
        """
        Generally gets field value. Since not all assessment versions have assessment aggregates,
        this ensures the application does not fail

        Returns:
            value : value of the field (many types possible)
        """
        if "assessmentVersion__assessmentaggregate" in field_name:
            #following code is taken from the source code for CSVExportView
            try:
                related_field_names = field_name.split('__')
                related_obj = getattr(obj, related_field_names[0])
                related_field_name = '__'.join(related_field_names[1:])
                return self.get_field_value(related_obj, related_field_name)
            except:
                return ""
        else:
            return super(OutputCSVDepartment,self).get_field_value(obj, field_name)
    def get_queryset(self):
        """
        Gets the QuerySet of AssessmentData to generate the CSV for.
        In particular, it limits to assessments within the year within the department.
        
        Returns:
            QuerySet : set of AssessmentData within parameters
        """
        return AssessmentData.objects.filter(
            assessmentVersion__report__year__gte=self.kwargs['gYear'],
            assessmentVersion__report__year__lte=self.kwargs['lYear'],
            assessmentVersion__report__degreeProgram__department__pk=self.kwargs['dept'])
    def test_func(self):
        """
        Ensures the user is in the department or the AAC

        Returns:
            bool : whether user can access the page
        """
        return (self.request.user.profile.department.pk == int(self.kwargs['dept'])) or self.request.user.profile.aac
class OutputCSVDP(OutputCSVDepartment):
    """
    View to generate CSV for a specific degree program within given years

    Keyword Args:
        gYear (str): the minimum year for data
        lYear (str): the maximum year for data
        dept (str): the primary key of the desired department
        dP (str): the primary key of the desired degree program
    """
    def get_queryset(self):
        """
        Gets the QuerySet to generate CSV for, filtering based upon year and degree program
        
        Returns:
            QuerySet : set of AssessmentData within parameters
        """
        return AssessmentData.objects.filter(
            assessmentVersion__report__year__gte=self.kwargs['gYear'],
            assessmentVersion__report__year__lte=self.kwargs['lYear'],
            assessmentVersion__report__degreeProgram__pk=self.kwargs['dP'])
class OutputCSVCollege(OutputCSVDepartment):
    """
    View to output CSV for data within a specific college

    Keyword Args:
        gYear (str): the minimum year for data
        lYear (str): the maximum year for data
        col (str): the primary key of the desired college
    """
    fields = [
        'assessmentVersion__report__year',
        'assessmentVersion__report__degreeProgram__department', 'assessmentVersion__report__degreeProgram__department__name',
        'assessmentVersion__report__degreeProgram', 'assessmentVersion__report__degreeProgram__name',
        'assessmentVersion__report',
        'assessmentVersion__slo', 'assessmentVersion__slo__goalText', 'assessmentVersion__slo__changedFromPrior',
        'assessmentVersion__slo__slo__blooms', 'assessmentVersion__slo__slo',
        'assessmentVersion__assessment', 'assessmentVersion__assessment__title',
        'assessmentVersion__assessment__domainExamination', 
        'assessmentVersion__assessment__domainProduct', 
        'assessmentVersion__assessment__domainPerformance',
        'assessmentVersion__assessment__directMeasure',
        'assessmentVersion', 'assessmentVersion__assessmentaggregate__aggregate_proficiency',
        'assessmentVersion__assessmentaggregate__met',
        'assessmentVersion__date', 'assessmentVersion__description',
        'assessmentVersion__finalTerm', 'assessmentVersion__where',
        'assessmentVersion__allStudents', 'assessmentVersion__sampleDescription',
        'assessmentVersion__frequencyChoice', 'assessmentVersion__frequency',
        'assessmentVersion__threshold', 'assessmentVersion__target', 'assessmentVersion__changedFromPrior',
        'dataRange','numberStudents','overallProficient',
        ]
    def get_queryset(self):
        """
        Gets the QuerySet to generate CSV for, filtering based upon year and college
        
        Returns:
            QuerySet : set of AssessmentData within parameters
        """
        return AssessmentData.objects.filter(
            assessmentVersion__report__year__gte=self.kwargs['gYear'],
            assessmentVersion__report__year__lte=self.kwargs['lYear'],
            assessmentVersion__report__degreeProgram__department__college__pk=self.kwargs['col']
            )
    def test_func(self):
        """
        Ensures the user is within the AAC

        Returns:
            bool : whether the user is in the AAC and therefore can access the page
        """
        return self.request.user.profile.aac
class CSVManagement(LoginRequiredMixin, TemplateView):
    """
    View to set parameters to generate CSV from one of the other views
    """
    template_name = "makeReports/CSV/csvManagement.html"
    def get_context_data(self, **kwargs):
        """
        Gets active colleges needed to display page

        Returns:
            context (dict): dictionary of context for template, including active colleges
        """
        context = super(CSVManagement, self).get_context_data(**kwargs)
        context['colleges'] = College.active_objects.all().order_by("name")
        return context