"""
This file contains all view related to inputting SLOs into the form
"""
from datetime import datetime
from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, FormView
from django.urls import reverse_lazy
from makeReports.models import AssessmentVersion, DegreeProgram, Report, SLO, SLOInReport, SLOsToStakeholder
from makeReports.forms import CreateNewSLO, EditImportedSLOForm, ImportSLOForm, ImportStakeholderForm, Single2000Textbox
from makeReports.views.helperFunctions.mixins import DeptReportMixin
from .helperFunctions.todos import todoGetter

class SLOSummary(DeptReportMixin,ListView):
    """
    View to summarize SLO while entering information
    """
    model = SLOInReport
    template_name ="makeReports/SLO/sloSummary.html"
    context_object_name = "slo_list"
    def get_queryset(self):
        """
        Gets SLOs in report ordered by number

        Returns:
            QuerySet : SLOs (:class:`~makeReports.models.slo_models.SLOInReport`) in report
        """
        report = self.report
        objs = SLOInReport.objects.filter(report=report).order_by("number")
        return objs
    def get_context_data(self, **kwargs):
        """
        Gets template context, including the stakeholder communication

        Returns:
            dict : context for template
        """
        context = super(SLOSummary, self).get_context_data()
        context['stk'] = SLOsToStakeholder.objects.filter(report=self.report).last()
        context['toDo'] = todoGetter(1,self.report)
        context['reqTodo'] = len(context['toDo']['r'])
        context['sugTodo'] = len(context['toDo']['s'])
        return context
class AddNewSLO(DeptReportMixin,FormView):
    """
    View to add a new SLO
    """
    template_name = "makeReports/SLO/addSLO.html"
    form_class = CreateNewSLO
    def get_form_kwargs(self):
        """
        Returns keyword arguments for form, including whether the degree program is graduate level

        Returns:
            dict : keyword arguments for form
        """
        kwargs = super(AddNewSLO,self).get_form_kwargs()
        if self.report.degreeProgram.level == "GR":
            kwargs['grad'] = True
        else:
            kwargs['grad'] = False
        return kwargs
    def get_success_url(self):
        """
        Gets URL to go to upon success (SLO summary)

        Returns:
            str : URL of SLO summary page (:class:`~makeReports.views.slo_views.SLOSummary`)
        """
        return reverse_lazy('makeReports:slo-summary', args=[self.report.pk])
    def form_valid(self, form):
        """
        Creates SLO from form, updates report's field numberOrSLOs

        Args:
            form (CreateNewSLO): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        try:
            gGoals = form.cleaned_data["gradGoals"]
        except:
            gGoals = []
        rpt = self.report
        sloObj = SLO.objects.create(blooms=form.cleaned_data['blooms'])
        for gg in gGoals:
            sloObj.gradGoals.add(gg)
        num = self.report.numberOfSLOs
        num += 1
        sloRpt = SLOInReport.objects.create(
            date=datetime.now(), 
            goalText =form.cleaned_data['text'], 
            slo=sloObj, 
            changedFromPrior=False, 
            report=rpt, 
            number = num
            )
        sloObj.save()
        sloRpt.save()
        return super(AddNewSLO, self).form_valid(form)
class ImportSLO(DeptReportMixin,FormView):
    """
    View to import pre-existing SLO

    Notes:
        Search parameters 'year' and 'dp' (primary key of degree program) passed in get request
    """
    template_name = "makeReports/SLO/importSLO.html"
    form_class = ImportSLOForm
    def get_success_url(self):
        """
        Gets URL to go to upon success (SLO summary)

        Returns:
            str : URL of SLO summary page (:class:`~makeReports.views.slo_views.SLOSummary`)
        """
        return reverse_lazy('makeReports:slo-summary', args=[self.report.pk])
    def get_form_kwargs(self):
        """
        Get keyword arguments for form, including SLOs meeting search parameters

        Returns:
            dict : keyword arguments for form
        """
        kwargs = super(ImportSLO,self).get_form_kwargs()
        yearIn = self.request.GET['year']
        try:
            dPobj = DegreeProgram.objects.get(pk=self.request.GET['dp'])
        except DegreeProgram.DoesNotExist:
            raise Http404("Degree program matching URL does not exist.")
        sloChoices = SLOInReport.objects.filter(
            report__year=yearIn, 
            report__degreeProgram=dPobj
            ).order_by("number")
        slosInReport = SLOInReport.objects.filter(report=self.report).order_by("number")
        for slo in slosInReport:
            sloChoices = sloChoices.exclude(slo=slo.slo)
        kwargs['sloChoices'] = sloChoices
        return kwargs
    def form_valid(self,form):
        """
        Import SLO and assessments based upon form, also updates numberOfSLOs field in report
        
        Args:
            form (ImportSLOForm): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        rpt = self.report
        num = rpt.numberOfSLOs
        for sloInRpt in form.cleaned_data['slo']:
            num += 1
            newS = SLOInReport.objects.create(
                date=datetime.now(),
                number=num,
                goalText=sloInRpt.goalText,
                slo=sloInRpt.slo,
                report=rpt, 
                changedFromPrior=False)
            if form.cleaned_data['importAssessments']:
                    assessSet = AssessmentVersion.objects.filter(slo=sloInRpt)
                    for assess in assessSet:
                        newA = AssessmentVersion.objects.create(
                            report=self.report,
                            slo = newS,
                            number=newS.numberOfAssess+1,
                            changedFromPrior=False,
                            assessment = assess.assessment,
                            date = datetime.now(),
                            description = assess.description,
                            finalTerm = assess.finalTerm,
                            where = assess.where,
                            allStudents = assess.allStudents,
                            sampleDescription = assess.sampleDescription,
                            frequencyChoice = assess.frequencyChoice,
                            frequency = assess.frequency,
                            threshold = assess.threshold,
                            target = assess.target
                            )
                        for aSup in assess.supplements.all():
                            newA.supplements.add(aSup)
                        newA.save()
        return super(ImportSLO,self).form_valid(form)
    def get_context_data(self, **kwargs):
        """
        Returns context for template, including the current degree program and those within the department

        Returns:
            dict : context for template
        """
        context = super(ImportSLO, self).get_context_data(**kwargs)
        r = self.report
        context['currentDPpk'] = Report.objects.get(pk=self.kwargs['report']).degreeProgram.pk
        context['degPro_list'] = DegreeProgram.objects.filter(department=r.degreeProgram.department)
        return context
class EditImportedSLO(DeptReportMixin,FormView):
    """
    View to edit imported SLO (more restricted than new SLO)

    Keyword Args:
        sloIR (str): primary key of :class:`~makeReports.models.slo_models.SLOInReport` to edit
    """
    template_name = "makeReports/SLO/editImportedSLO.html"
    form_class = EditImportedSLOForm
    def dispatch(self,request,*args,**kwargs):
        """
        Dispatches view and attaches :class:`~makeReports.models.slo_models.SLOInReport` to instance

        Args:
            request (HttpRequest): request to view page
        
        Keyword Args:
            sloIR (str): primary key of :class:`~makeReports.models.slo_models.SLOInReport` to edit
            
        Returns:
            HttpResponse : response of page to request
        """
        try:
            self.sloInRpt = SLOInReport.objects.get(pk=self.kwargs['sloIR'])
        except SLOInReport.DoesNotExist:
            raise Http404("Report matching URL does not exist.")
        return super(EditImportedSLO,self).dispatch(request,*args,**kwargs)
    def get_initial(self):
        """
        Gets initial form values, including goal text from current values

        Returns:
            dict : initial form values
        """
        initial = super(EditImportedSLO, self).get_initial()
        initial['text'] = self.sloInRpt.goalText
        return initial
    def get_success_url(self):
        """
        Gets URL to go to upon success (SLO summary)

        Returns:
            str : URL of SLO summary page (:class:`~makeReports.views.slo_views.SLOSummary`)
        """
        return reverse_lazy('makeReports:slo-summary', args=[self.report.pk])
    def form_valid(self,form):
        """
        Edits SLO from form

        Args:
            form (EditImportedSLOForm): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        self.sloInRpt.date=datetime.now()
        self.sloInRpt.goalText=form.cleaned_data['text']
        self.sloInRpt.changedFromPrior = True
        self.sloInRpt.save()
        return super(EditImportedSLO, self).form_valid(form)
class EditNewSLO(DeptReportMixin,FormView):
    """
    View to edit new SLO (not-restricted)

    Keyword Args:
        sloIR (str): primary key of :class:`~makeReports.models.slo_models.SLOInReport` to edit
    """
    template_name = "makeReports/SLO/editNewSLO.html"
    form_class = CreateNewSLO
    def dispatch(self,request,*args,**kwargs):
        """
        Dispatches view and attaches :class:`~makeReports.models.slo_models.SLOInReport` to instance

        Args:
            request (HttpRequest): request to view page
        
        Keyword Args:
            sloIR (str): primary key of :class:`~makeReports.models.slo_models.SLOInReport` to edit
            
        Returns:
            HttpResponse : response of page to request
        """
        try:
            self.sloInRpt = SLOInReport.objects.get(pk=self.kwargs['sloIR'], slo__numberOfUses=1)
        except SLOInReport.DoesNotExist:
            raise Http404("SLO matching URL does not exist.")
        return super(EditNewSLO,self).dispatch(request,*args,**kwargs)
    def get_form_kwargs(self):
        """
        Gets keyword arguments for form, including whether it is graduate-level

        Returns:
            dict : form keyword arguments
        """
        kwargs = super(EditNewSLO,self).get_form_kwargs()
        if self.report.degreeProgram.level == "GR":
            kwargs['grad'] = True
            self.grad = True
        else:
            kwargs['grad'] = False
            self.grad = False
        return kwargs
    def get_initial(self):
        """
        Gets initial values for the form based upon current values

        Returns:
            dict : initial form values
        """
        initial = super(EditNewSLO, self).get_initial()
        initial['text'] = self.sloInRpt.goalText
        initial['blooms'] = self.sloInRpt.slo.blooms
        initial['gradGoals'] = self.sloInRpt.slo.gradGoals.all
        return initial
    def get_success_url(self):
        """
        Gets URL to go to upon success (SLO summary)

        Returns:
            str : URL of SLO summary page (:class:`~makeReports.views.slo_views.SLOSummary`)
        """
        return reverse_lazy('makeReports:slo-summary', args=[self.report.pk])
    def form_valid(self, form):
        """
        Update SLO based upon the form

        Args:
            form (CreateNewSLO): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        self.sloInRpt.goalText = form.cleaned_data['text']
        self.sloInRpt.date = datetime.now()
        self.sloInRpt.slo.blooms = form.cleaned_data['blooms']
        if self.grad:
            for gg in form.cleaned_data['gradGoals']:
                self.sloInRpt.slo.gradGoals.add(gg)
        self.sloInRpt.save()
        self.sloInRpt.slo.save()
        return super(EditNewSLO,self).form_valid(form)
class StakeholderEntry(DeptReportMixin,FormView):
    """
    View to enter how SLOs are communicated to stakeholders
    """
    template_name = "makeReports/SLO/stakeholdersSLO.html"
    form_class = Single2000Textbox
    def dispatch(self,request,*args,**kwargs):
        """
        Dispatches view and attaches
         current stakeholder communication (:class:`~makeReports.models.slo_models.SLOsToStakeholder`) to instance
        
        Args:
            request (HttpRequest): request to view page
            
        Returns:
            HttpResponse : response of page to request
        
        Keyword Args:
            report (str): primary key of report
        
        """
        self.sts = SLOsToStakeholder.objects.filter(report__pk=self.kwargs['report']).last()
        return super(StakeholderEntry,self).dispatch(request,*args,**kwargs)
    def get_success_url(self):
        """
        Gets URL to go to upon success (SLO summary)

        Returns:
            str : URL of SLO summary page (:class:`~makeReports.views.slo_views.SLOSummary`)
        """
        return reverse_lazy('makeReports:slo-summary', args=[self.report.pk])
    def get_initial(self):
        """
        Initializes form value based upon current values
        
        Returns:
            dict : initial form values
        """
        initial = super(StakeholderEntry,self).get_initial()
        try:
            #if sts:
            initial['text']=self.sts.text
        except:
            pass
        return initial
    def form_valid(self,form):
        """
        Updates or creates stakeholder communication

        Args:
            form (Single2000Textbox): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        try:
            self.sts.text = form.cleaned_data['text']
            self.sts.save()
        except Exception:
            SLOsToStakeholder.objects.create(text=form.cleaned_data['text'], report=self.report)
        return super(StakeholderEntry,self).form_valid(form)
class ImportStakeholderEntry(DeptReportMixin,FormView):
    """
    View to import stakeholder communication from within department
    
    Notes:
        Search parameters 'dp' for degree program primary key and 'year' sent through get request
    """
    template_name = "makeReports/SLO/importStakeholderComm.html"
    form_class = ImportStakeholderForm
    def get_success_url(self):
        """
        Gets URL to go to upon success (Communicating to Stakeholders)

        Returns:
            str : URL of communicating to stakeholders page (:class:`~makeReports.views.slo_views.StakeholderEntry`)
        """
        return reverse_lazy('makeReports:slo-stakeholders', args=[self.report.pk])
    def get_form_kwargs(self):
        """
        Get keyword arguments for form, including stakeholder communications that match search parameters

        Returns:
            dict : form keyword arguments
        """
        kwargs = super(ImportStakeholderEntry,self).get_form_kwargs()
        yearIn = self.request.GET['year']
        try:
            dPobj = DegreeProgram.objects.get(pk=self.request.GET['dp'])
        except DegreeProgram.DoesNotExist:
            raise Http404("Degree program matching URL does not exist.")
        kwargs['stkChoices'] = SLOsToStakeholder.objects.filter(report__year=yearIn, report__degreeProgram=dPobj)
        return kwargs
    def form_valid(self,form):
        """
        Imports stakeholder communication or creates new one in case of error

        Args:
            form (ImportStakeholderForm): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        oldSTS = form.cleaned_data["stk"]
        try:
            sts = SLOsToStakeholder.objects.filter(report=self.report).first()
            if oldSTS.report == self.report:
                pass
            elif sts:
                sts.text = form.cleaned_data['stk'].text
                sts.save()
            else:
                SLOsToStakeholder.objects.create(text=form.cleaned_data['stk'].text, report=self.report)
        except:
            SLOsToStakeholder.objects.create(text=form.cleaned_data['stk'].text, report=self.report)
        return super(ImportStakeholderEntry,self).form_valid(form)
    def get_context_data(self, **kwargs):
        """
        Gets context for template, including current degree program and all degree programs within department

        Returns:
            dict : context for template
        """
        context = super(ImportStakeholderEntry, self).get_context_data(**kwargs)
        context['currentDPpk'] = self.report.degreeProgram.pk
        context['degPro_list'] = DegreeProgram.objects.filter(department=self.report.degreeProgram.department)
        return context
class Section1Comment(DeptReportMixin,FormView):
    """
    View to enter comment for section 1 of the report
    """
    template_name = "makeReports/SLO/sloComment.html"
    form_class = Single2000Textbox
    def get_success_url(self):
        """
        Gets URL to go to upon success (SLO summary)

        Returns:
            str : URL of SLO summary page (:class:`~makeReports.views.slo_views.SLOSummary`)
        """
        return reverse_lazy('makeReports:slo-summary', args=[self.report.pk])
    def form_valid(self, form):
        """
        Saves comment to report 

        Args:
            form (Single2000Textbox): filled out form to process

        Returns:
            HttpResponseRedirect : redirects to success URL
        """
        self.report.section1Comment = form.cleaned_data['text']
        self.report.save()
        return super(Section1Comment,self).form_valid(form)
    def get_initial(self):
        """
        Initializes the form with "No Commment"
        Returns:
            dict : initial values for form
        """
        initial = super(Section1Comment,self).get_initial()
        initial['text']="No comment."
        if self.report.section1Comment:
            initial['text'] = self.report.section1Comment
        return initial
class DeleteImportedSLO(DeptReportMixin,DeleteView):
    """
    View to delete imported SLO (does not delete super SLO)

    Keyword Args:
        pk (str): primary key of :class:`~makeReports.models.slo_models.SLOInReport` to delete
    """
    model = SLOInReport
    template_name = "makeReports/SLO/deleteSLO.html"
    def get_object(self, queryset=None):
        """ Hook to ensure it is an imported SLO """
        obj = super(DeleteImportedSLO, self).get_object()
        if not obj.slo.numberOfUses>1:
            raise Http404("Imported SLO matching does not exist.")
        return obj
    def get_success_url(self):
        """
        Gets the success URL (SLO summary)

        Returns:
            str : URL of SLO summary page (:class:`~makeReports.views.slo_views.SLOSummary`)
        """ 
        return reverse_lazy('makeReports:slo-summary', args=[self.report.pk])
class DeleteNewSLO(DeptReportMixin,DeleteView):
    """
    View to delete new SLO (deletes the super SLO as well)

    Keyword Args:
        pk (str): primary key of :class:`~makeReports.models.slo_models.SLOInReport` to delete
    """
    model = SLOInReport
    template_name = "makeReports/SLO/deleteSLO.html"
    def get_object(self, queryset=None):
        """ Hook to ensure it is a new SLO """
        obj = super(DeleteNewSLO, self).get_object()
        if obj.slo.numberOfUses>1:
            raise Http404("New SLO matching does not exist.")
        return obj
    def get_success_url(self):
        """
        Gets success URL (SLO summary)
        
        Returns:
            str : URL of SLO summary page (:class:`~makeReports.views.slo_views.SLOSummary`)
        """
        return reverse_lazy('makeReports:slo-summary', args=[self.report.pk])

