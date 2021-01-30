"""
This file contains all views related to inputting assessments into the form
"""
from datetime import datetime
from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, FormView
from django.urls import reverse_lazy
from makeReports.models import (
    Assessment,
    AssessmentVersion,
    AssessmentSupplement,
    DegreeProgram,
    SLOInReport
)
from makeReports.forms import (
    CreateNewAssessment,
    EditImportedAssessmentForm,
    EditNewAssessmentForm,
    ImportAssessmentForm,
    ImportSupplementsForm,
    Single2000Textbox
)
from .helperFunctions.section_context import section2Context
from .helperFunctions.mixins import DeptReportMixin
from .helperFunctions.todos import todoGetter

class AssessmentSummary(DeptReportMixin,ListView):
    """
    View to summarize state of assessment section of form
    """
    model = AssessmentVersion
    template_name = "makeReports/Assessment/assessmentSummary.html"
    context_object_name = "assessment_list"
    def get_queryset(self):
        """
        Returns assessments in report ordered by SLO

        Returns:
            QuerySet : :class:`~makeReports.models.assessment_models.AssessmentVersion` objects in report
        """
        report = self.report
        objs = AssessmentVersion.objects.filter(report=report).order_by("slo__number","number")
        return objs
    def get_context_data(self, **kwargs):
        """
        Gets context for template

        Notes:
            calls section2Context to retrieve context needed
        Returns:
            dict : context for template
        """
        context = super(AssessmentSummary, self).get_context_data()
        context['toDo'] = todoGetter(2,self.report)
        context['reqTodo'] = len(context['toDo']['r'])
        context['sugTodo'] = len(context['toDo']['s'])
        return section2Context(self,context)
class AddNewAssessment(DeptReportMixin,FormView):
    """
    View to add a new assessment
    """

    template_name = "makeReports/Assessment/addAssessment.html"
    form_class = CreateNewAssessment
    def get_form_kwargs(self):
        """
        Gets keyword arguments for form, only allowing for SLOs in report
        
        Returns:
            dict : keyword arguments for form
        """
        kwargs = super(AddNewAssessment,self).get_form_kwargs()
        kwargs['sloQS'] = SLOInReport.objects.filter(report=self.report).order_by("number")
        kwargs['useaccform'] = self.report.accredited
        return kwargs
    def get_success_url(self):
        """
        Gets assessment summary url (assessment summary)

        Returns:
            str : success url of success page (:class:`~makeReports.views.assessment_views.AssessmentSummary`)
        """
        return reverse_lazy('makeReports:assessment-summary', args=[self.report.pk])
    def form_valid(self, form):
        """
        |  Creates :class:`~makeReports.models.assessment_models.Assessment` and :class:`~makeReports.models.assessment_models.AssessmentVersion` based upon form
        |  Updates the numberOfAssess fields for :class:`~makeReports.models.slo_models.SLO`

        Args:
            form (CreateNewAssessment): completed form to be processed
            
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        rpt = self.report
        if not rpt.accredited:
            assessObj = Assessment.objects.create(
                title=form.cleaned_data['title'], 
                domainExamination=False, 
                domainProduct=False, 
                domainPerformance=False, 
                directMeasure=form.cleaned_data['directMeasure'])
            assessRpt = AssessmentVersion.objects.create(
                date=datetime.now(), 
                number = form.cleaned_data['slo'].numberOfAssess+1, 
                assessment=assessObj, 
                description=form.cleaned_data['description'], 
                finalTerm=form.cleaned_data['finalTerm'], 
                where=form.cleaned_data['where'], 
                allStudents=form.cleaned_data['allStudents'], 
                sampleDescription=form.cleaned_data['sampleDescription'], 
                frequency=form.cleaned_data['frequency'], 
                frequencyChoice = form.cleaned_data['frequencyChoice'],
                threshold=form.cleaned_data['threshold'], 
                target=form.cleaned_data['target'],
                slo=form.cleaned_data['slo'],
                report=rpt, 
                changedFromPrior=False)
        else:
            assessObj = Assessment.objects.create(
                title=form.cleaned_data['title'], 
                domainExamination=False, 
                domainProduct=False, 
                domainPerformance=False, 
                directMeasure=True)
            assessRpt = AssessmentVersion.objects.create(
                date=datetime.now(), 
                number = form.cleaned_data['slo'].numberOfAssess+1, 
                assessment=assessObj, 
                description='Ignore - Accredited Form',
                finalTerm=True,
                where='Ignore - Accredited Form',
                allStudents=True,
                sampleDescription='Ignore - Accredited Form',
                frequency=form.cleaned_data['frequency'], 
                frequencyChoice = form.cleaned_data['frequencyChoice'],
                threshold='Ignore - Accredited Form',
                target=0,
                slo=form.cleaned_data['slo'],
                report=rpt, 
                changedFromPrior=False)

        dom = form.cleaned_data['domain']
        if ("Pe" in dom):
            assessObj.domainPerformance = True
        if ("Pr" in dom):
            assessObj.domainProduct = True
        if ("Ex" in dom):
            assessObj.domainExamination = True
        assessObj.save()
        assessRpt.save()
        return super(AddNewAssessment, self).form_valid(form)
class AddNewAssessmentSLO(AddNewAssessment):
    """
    View to add new assessment from the SLO page
    
    Keyword Args:
        slo (str): primary key of :class:`~makeReports.models.slo_models.SLO` to add assessment
    """
    def get_initial(self):
        """
        Initializes slo of form to that of the page this view was navigated from

        Returns:
            dict : initial form values
        """
        initial = super(AddNewAssessmentSLO,self).get_initial()
        initial['slo'] = SLOInReport.objects.get(pk=self.kwargs['slo'])
        return initial
    def get_success_url(self):
        """
        Gets URL to go to upon success (SLO summary)

        Returns:
            str : URL of SLO summary page (:class:`~makeReports.views.slo_views.SLOSummary`)
        """
        return reverse_lazy('makeReports:slo-summary', args=[self.report.pk])
class ImportAssessment(DeptReportMixin,FormView):
    """
    View to import assessment from within the department

    Notes:
        Through get request URL, the following search parameters are sent:
        'year','dp: primary key of degree program, 'slo': primary key of SLO (:class:`~makeReports.models.slo_models.SLOInReport`)
    """
    template_name = "makeReports/Assessment/importAssessment.html"
    form_class = ImportAssessmentForm
    def get_success_url(self):
        """
        Gets URL to go to upon success (assessment summary)

        Returns:
            str : URL of assessment summary page (:class:`~makeReports.views.assessment_views.AssessmentSummary`)
        """
        return reverse_lazy('makeReports:assessment-summary', args=[self.report.pk])
    def get_form_kwargs(self):
        """
        Get keyword arguments of form, by filtering the assessment choices by search parameters,
        and SLO choices by the report

        Returns:
            dict : keyword arguments of the form
        """
        kwargs = super(ImportAssessment,self).get_form_kwargs()
        keys = self.request.GET.keys()
        aCs = AssessmentVersion.objects
        if 'year' in keys:
            yearIn = self.request.GET['year']
            if yearIn!="":
                aCs=aCs.filter(report__year=yearIn)
        if 'dp' in keys:
            dP = self.request.GET['dp']
            if dP!="" and dP!="-1":
                try:
                    aCs=aCs.filter(report__degreeProgram=DegreeProgram.objects.get(pk=dP))
                except:
                    pass
        if 'slo' in keys:
            if self.request.GET['slo']!="" and self.request.GET['slo']!="-1":
                aCs=aCs.filter(slo=SLOInReport.objects.get(pk=self.request.GET['slo']))
        kwargs['assessChoices'] = aCs
        kwargs['slos'] = SLOInReport.objects.filter(report=self.report).order_by("number")
        return kwargs
    def form_valid(self,form):
        """
        |  Creates :class:`~makeReports.models.assessment_models.AssessmentVersion` from form
        
        Args:
            form (ImportAssessmentForm): completed form to be processed
            
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        
        """
        rpt = self.report
        slo = form.cleaned_data['slo']
        num = slo.numberOfAssess
        for assessVers in form.cleaned_data['assessment']:
            num += 1
            AssessmentVersion.objects.create(
                slo=slo,
                number=num,
                date=datetime.now(), 
                description=assessVers.description,
                assessment=assessVers.assessment, 
                report=rpt, 
                changedFromPrior=False, 
                finalTerm=assessVers.finalTerm, 
                where=assessVers.where, 
                allStudents=assessVers.allStudents, 
                sampleDescription=assessVers.sampleDescription, 
                frequencyChoice = assessVers.frequencyChoice,
                frequency=assessVers.frequency, 
                threshold=assessVers.threshold, 
                target=assessVers.target)
        return super(ImportAssessment,self).form_valid(form)
    def get_context_data(self, **kwargs):
        """
        Gets context for template, with the current degree program, all degree programs within the department, and SLOs within department

        Returns:
            dict : context for template

        Notes:
            Arranges SLOs by first those which appear within this report, and then all others
        """
        context = super(ImportAssessment, self).get_context_data(**kwargs)
        r = self.report
        context['currentDPpk'] = r.degreeProgram.pk
        context['degPro_list'] = DegreeProgram.objects.filter(department=r.degreeProgram.department)
        return context
class ImportAssessmentSLO(ImportAssessment):
    """
    Imports assessment for a specific SLO
    
    Keyword Args:
        slo (str) : primary key of :class:`~makeReports.models.slo_models.SLOInReport`
    """
    template_name = "makeReports/Assessment/importAssessmentSLO.html"
    def dispatch(self,request,*args,**kwargs):
        """
        Dispatches the view, and attaches the specific :class:`~makeReports.models.slo_models.SLOInReport` to the instance

        Args:
            request (HttpRequest): request to view page
        Keyword Args:
            slo (str) : primary key of :class:`~makeReports.models.slo_models.SLOInReport`
            
        Returns:
            HttpResponse : response of page to request
        """
        try:
            self.slo = SLOInReport.objects.get(pk=self.kwargs['slo'])
        except SLOInReport.DoesNotExist:
            raise Http404("No SLO matches the URL.")
        return super(ImportAssessmentSLO,self).dispatch(request,*args,**kwargs)
    def get_success_url(self):
        """
        Gets URL to go to upon success (SLO summary)

        Returns:
            str : URL of SLO summary page (:class:`~makeReports.views.slo_views.SLOSummary`)
        """
        return reverse_lazy('makeReports:slo-summary', args=[self.report.pk])
    def get_initial(self):
        """
        Initializes the form, sets the SLO appropriately

        Returns:
            dict : initial form values
        """
        initial = super(ImportAssessmentSLO,self).get_initial()
        initial['slo'] = self.slo
        return initial
    def get_context_data(self, **kwargs):
        """
        Gets context for the template, and attaches the :class:`~makeReports.models.slo_models.SLOInReport` to the context

        Returns:
            dict : context for template
        """
        context = super(ImportAssessmentSLO, self).get_context_data(**kwargs)
        context['slo'] = self.slo
        return context
class EditImportedAssessment(DeptReportMixin,FormView):
    """
    View to edit imported assessment (cannot change fields in :class:`~makeReports.models.assessment_models.Assessment`)
    
    Keyword Args:
        assessIR (str): primary key of :class:`~makeReports.models.assessment_models.AssessmentVersion` to update
    """
    template_name = "makeReports/Assessment/editImportedAssessment.html"
    form_class = EditImportedAssessmentForm
    def dispatch(self,request,*args,**kwargs):
        """
        Dispatches view, and attaches :class:`~makeReports.models.assessment_models.AssessmentVersion` to instance

        Args:
            request (HttpRequest): request to view page
        
        Keyword Args:
            assessIR (str): primary key of :class:`~makeReports.models.assessment_models.AssessmentVersion` to update
        
        Returns:
            HttpResponse : response of page to request
        """
        try:
            self.assessVers = AssessmentVersion.objects.get(pk=self.kwargs['assessIR'])
        except AssessmentVersion.DoesNotExist:
            raise Http404("No asssessment matches the URL.")
        return super(EditImportedAssessment,self).dispatch(request,*args,**kwargs)
    def get_initial(self):
        """
        Gets initial form values based upon the current values of the :class:`~makeReports.models.assessment_models.AssessmentVersion`
        
        Returns:
            dict : initial form values
        """
        initial = super(EditImportedAssessment, self).get_initial()
        initial['description'] = self.assessVers.description
        initial['finalTerm'] = self.assessVers.finalTerm
        initial['where'] = self.assessVers.where
        initial['allStudents'] = self.assessVers.allStudents
        initial['sampleDescription'] = self.assessVers.sampleDescription
        initial['frequencyChoice'] = self.assessVers.frequencyChoice
        initial['frequency'] = self.assessVers.frequency
        initial['threshold'] = self.assessVers.threshold
        initial['target'] = self.assessVers.target
        initial['slo'] = self.assessVers.slo
        return initial
    def get_form_kwargs(self):
        """
        Gets form keywords, settings SLO options to those within the report

        Returns:
            dict : form keyword arguments
        """
        kwargs = super(EditImportedAssessment,self).get_form_kwargs()
        kwargs['sloQS'] = SLOInReport.objects.filter(report=self.report).order_by("number")
        kwargs['useaccform'] = self.report.accredited
        return kwargs
    def get_success_url(self):
        """
        Gets URL to go to upon success (assessment summary)

        Returns:
            str : URL of assessment summary page (:class:`~makeReports.views.assessment_views.AssessmentSummary`)
        """
        return reverse_lazy('makeReports:assessment-summary', args=[self.report.pk])
    def form_valid(self,form):
        """
        Edits imported assessment based upon form

        Args:
            form (EditImportedAssessmentForm): completed form to be processed
            
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        self.assessVers.description = form.cleaned_data['description']
        self.assessVers.date = datetime.now()
        self.assessVers.finalTerm = form.cleaned_data['finalTerm']
        self.assessVers.where = form.cleaned_data['where']
        self.assessVers.allStudents = form.cleaned_data['allStudents']
        self.assessVers.sampleDescription = form.cleaned_data['sampleDescription']
        self.assessVers.frequencyChoice = form.cleaned_data['frequencyChoice']
        self.assessVers.frequency = form.cleaned_data['frequency']
        self.assessVers.threshold = form.cleaned_data['threshold']
        self.assessVers.target = form.cleaned_data['target']
        self.assessVers.changedFromPrior = True
        if self.assessVers.slo != form.cleaned_data['slo']:
            slo = self.assessVers.slo
            oldNum = self.assessVers.number
            assess = AssessmentVersion.objects.filter(report=self.report,slo=slo).exclude(pk=self.assessVers.pk)
            for a in assess:
                if a.number > oldNum:
                    a.number -= 1
                    a.save()
            slo.numberOfAssess -= 1
            slo.save()
            form.cleaned_data['slo'].numberOfAssess += 1
            self.assessVers.number = form.cleaned_data['slo'].numberOfAssess
            form.cleaned_data['slo'].save()
            self.assessVers.slo = form.cleaned_data['slo']
        self.assessVers.save()
        return super(EditImportedAssessment, self).form_valid(form)
class EditNewAssessment(EditImportedAssessment):
    """
    View to edit new assessments (can change fields in :class:`~makeReports.models.assessment_models.Assessment`)
    
    Keyword Args:
        assessIR (str): primary key of :class:`~makeReports.models.assessment_models.AssessmentVersion` to edit
    """
    template_name = "makeReports/Assessment/editNewAssessment.html"
    form_class = EditNewAssessmentForm
    def get_initial(self):
        """
        Get initial values of form based upon current values of the assessment

        Returns:
            dict : initial values of form
        """
        initial = super(EditNewAssessment, self).get_initial()
        initial['title'] = self.assessVers.assessment.title
        initial['domainPerformance'] = self.assessVers.assessment.domainPerformance
        initial['domainProduct'] = self.assessVers.assessment.domainProduct
        initial['domainExamination'] = self.assessVers.assessment.domainExamination
        initial['directMeasure'] = self.assessVers.assessment.directMeasure

        # domain: ['Pe', 'Pr', 'Ex']
        initial['domain'] = []
        if initial['domainPerformance']:
            initial['domain'].append('Pe')
        if initial['domainProduct']:
            initial['domain'].append('Pr')
        if initial['domainExamination']:
            initial['domain'].append('Ex')
        return initial
    def form_valid(self, form):
        """
        Edit assessment according to form

        Args:
            form (EditNewAssessmentForm) : form to be processed
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        if self.assessVers.assessment.numberOfUses >1:
            raise Http404("This assessment is imported elsewhere.")
        self.assessVers.assessment.title = form.cleaned_data['title']
        self.assessVers.assessment.domain = form.cleaned_data['domain']
        self.assessVers.assessment.directMeasure = form.cleaned_data['directMeasure']

        dom = form.cleaned_data['domain']
        self.assessVers.assessment.domainPerformance = "Pe" in dom
        self.assessVers.assessment.domainProduct = "Pr" in dom
        self.assessVers.assessment.domainExamination = "Ex" in dom
        self.assessVers.assessment.save()
        return super(EditNewAssessment,self).form_valid(form)
class SupplementUpload(DeptReportMixin,CreateView):
    """
    View to upload supplements to assessments

    Keyword Args:
        assessIR (str): primary key of :class:`~makeReports.models.assessment_models.AssessmentVersion`
    """
    template_name = "makeReports/Assessment/supplementUpload.html"
    model = AssessmentSupplement
    fields = ['supplement']
    def dispatch(self,request,*args,**kwargs):
        """
        Dispatch view and attach assessment to instance

        Args:
            request (HttpRequest): request to view page
        
        Keyword Args:
            assessIR (str): primary key of :class:`~makeReports.models.assessment_models.AssessmentVersion`
            
        Returns:
            HttpResponse : response of page to request
        """
        try:
            self.assessVers = AssessmentVersion.objects.get(pk=self.kwargs['assessIR'])
        except AssessmentVersion.DoesNotExist:
            raise Http404("No asssessment matches the URL.")
        return super(SupplementUpload,self).dispatch(request,*args,**kwargs)
    def get_success_url(self):
        """
        Gets success URL and used as hook to add supplement to assessment

        Returns:
            str : URL of assessment summary (:class:`~makeReports.views.assessment_views.AssessmentSummary`)
        """
        self.assessVers.supplements.add(self.object)
        self.assessVers.save()
        return reverse_lazy('makeReports:assessment-summary', args=[self.report.pk])
    def form_valid(self,form):
        """
        Sets the assessment version and datetime, then 
        creates supplement to assessment based upon form

        Args:
            form (ModelForm): completed form to process
            
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        form.instance.assessmentVersion = self.assessVers
        form.instance.uploaded_at = datetime.now()
        return super(SupplementUpload,self).form_valid(form)
class ImportSupplement(DeptReportMixin,FormView):
    """
    View to import supplement to assessment
    
    Keyword Args:
        assessIR (str): primary key of :class:`~makeReports.models.assessment_models.AssessmentVersion`
    
    Notes:
        Year and degree program to search for assessment passed via get request under
        'year' and 'dp' respectively
    """
    template_name = "makeReports/Assessment/importSupplement.html"
    form_class = ImportSupplementsForm
    def dispatch(self,request,*args,**kwargs):
        """
        Dispatches view and attaches :class:`~makeReports.models.assessment_models.AssessmentVersion` to instance

        Args:
            request (HttpRequest): request to view page
            
        Keyword Args:
            assessIR (str): primary key of :class:`~makeReports.models.assessment_models.AssessmentVersion`
        
        Returns:
            HttpResponse : response of page to request
        """
        try:
            self.assessVers = AssessmentVersion.objects.get(pk=self.kwargs['assessIR'])
        except AssessmentVersion.DoesNotExist:
            raise Http404("No asssessment matches the URL.")
        return super(ImportSupplement,self).dispatch(request,*args,**kwargs)
    def get_success_url(self):
        """
        Gets URL to go to upon success (assessment summary)

        Returns:
            str : URL of assessment summary page (:class:`~makeReports.views.assessment_views.AssessmentSummary`)
        """
        return reverse_lazy('makeReports:assessment-summary', args=[self.report.pk])
    def get_form_kwargs(self):
        """
        Gets form keyword arguments, set the supplement choices based upon search parameters

        Returns:
            dict : form keyword arguments
        """
        kwargs = super(ImportSupplement,self).get_form_kwargs()
        yearIn = self.request.GET['year']
        try:
            dPobj = DegreeProgram.objects.get(pk=self.request.GET['dp'])
        except DegreeProgram.DoesNotExist:
            raise Http404("No degree program matches the URL.")
        kwargs['supChoices'] = AssessmentSupplement.objects.filter(
            assessmentversion__report__year=yearIn, assessmentversion__report__degreeProgram=dPobj)
        return kwargs
    def form_valid(self,form):
        """
        Imports supplement to another assessment based upon form

        Args:
            form (ImportSupplementForm): completed form to be processed
            
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        self.assessVers.supplements.add(form.cleaned_data['sup'])
        self.assessVers.save()
        return super(ImportSupplement,self).form_valid(form)
    def get_context_data(self, **kwargs):
        """
        Gets context for template, passing the assessment, the current degree program, and degree programs within
        the department

        Returns:
            dict : context for template
        """
        context = super(ImportSupplement, self).get_context_data(**kwargs)
        context["aIR"] = self.kwargs['assessIR']
        context['currentDPpk'] = self.report.degreeProgram.pk
        context['degPro_list'] = DegreeProgram.objects.filter(department=self.report.degreeProgram.department)
        return context
class DeleteSupplement(DeptReportMixin,DeleteView):
    """
    View to delete supplement

    Keyword Args:
        pk (str): primary key of :class:`~makeReports.models.assessment_models.AssessmentSupplement` to delete
    """
    model = AssessmentSupplement
    template_name = "makeReports/Assessment/deleteSupplement.html"
    def get_success_url(self):
        """
        Gets URL to go to upon success (assessment summary)

        Returns:
            str : URL of assessment summary page (:class:`~makeReports.views.assessment_views.AssessmentSummary`)
        """
        return reverse_lazy('makeReports:assessment-summary', args=[self.report.pk])
class Section2Comment(DeptReportMixin,FormView):
    """
    View to add a comment for the second section of the form
    """
    template_name = "makeReports/Assessment/assessmentComment.html"
    form_class = Single2000Textbox
    def get_success_url(self):
        """
        Gets URL to go to upon success (assessment summary)

        Returns:
            str : URL of assessment summary page (:class:`~makeReports.views.assessment_views.AssessmentSummary`)
        """
        return reverse_lazy('makeReports:assessment-summary', args=[self.report.pk])
    def form_valid(self, form):
        """
        Sets the section 2 comment from the form

        Args:
            form (Single2000Textbox): completed form to be processed
            
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        self.report.section2Comment = form.cleaned_data['text']
        self.report.save()
        return super(Section2Comment,self).form_valid(form)
    def get_initial(self):
        """
        Gets initial value for form based upon current comment value

        Returns:
            dict : initial form values
        """
        initial = super(Section2Comment,self).get_initial()
        initial['text']="No comment."
        if self.report.section2Comment:
            initial['text'] = self.report.section2Comment
        return initial
class DeleteImportedAssessment(DeptReportMixin,DeleteView):
    """
    View to delete imported assessments (more restricted than new assessments)

    Keyword Args:
        pk (str): primary key of :class:`~makeReports.models.assessment_models.AssessmentVersion` to "delete"
    """
    model = AssessmentVersion
    template_name = "makeReports/Assessment/deleteAssessment.html"
    def get_object(self, queryset=None):
        """ Hook to ensure it is an imported assessment """
        obj = super(DeleteImportedAssessment, self).get_object()
        if not obj.assessment.numberOfUses>1:
            raise Http404("Imported assessment matching does not exist.")
        return obj
    def get_success_url(self):
        """
        Gets success url (assessment summary)

        Returns:
            str : URL of assessment summary (:class:`~makeReports.views.assessment_views.AssessmentSummary`)
        """
        return reverse_lazy('makeReports:assessment-summary', args=[self.report.pk])
class DeleteNewAssessment(DeptReportMixin,DeleteView):
    """
    View to delete new assessment

    Keyword Args:
        pk (str): primary key of :class:`~makeReports.models.assessment_models.AssessmentVersion` delete
    """
    model = AssessmentVersion
    template_name = "makeReports/Assessment/deleteAssessment.html"
    def get_object(self, queryset=None):
        """ Hook to ensure it is a new assessment """
        obj = super(DeleteNewAssessment, self).get_object()
        if obj.assessment.numberOfUses>1:
            raise Http404("New assessment matching URL does not exist.")
        return obj
    def get_success_url(self):
        """
        Gets success url (assessment summary page)

        Returns:
            str : assessment summary URL (:class:`~makeReports.views.assessment_views.AssessmentSummary`)
        """    
        return reverse_lazy('makeReports:assessment-summary', args=[self.report.pk])
