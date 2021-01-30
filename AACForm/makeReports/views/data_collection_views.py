"""
This file contains all views related to inputting data into the form
"""
from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from makeReports.models import (
    AssessmentAggregate,
    AssessmentData,
    AssessmentVersion,
    DataAdditionalInformation,
    ResultCommunicate,
    SLOInReport,
    SLOStatus
)
from makeReports.forms import (
    AddDataCollection, 
    AssessmentAggregateForm,
    SLOStatusForm, 
    ResultCommunicationForm,
    Single2000Textbox
)
from .helperFunctions.section_context import section3Context
from .helperFunctions.mixins import DeptReportMixin
from .helperFunctions.todos import todoGetter

class DataCollectionSummary(DeptReportMixin,ListView):
    """
    View to summarize data collection of in-progress form
    """
    model = AssessmentData
    template_name = 'makeReports/DataCollection/dataCollectionSummary.html'
    context_object_name = "data_collection_dict"
    def get_queryset(self):
        """
        Gets QuerySet of data objects that go with the report

        Returns:
            QuerySet : data (:class:`~makeReports.models.data_models.AssessmentData`) within the report
        """
        report = self.report
        assessments = AssessmentVersion.objects.filter(report=report).order_by("slo__number","number")
        assessment_qs = AssessmentData.objects.none()
        for assessment in assessments:
            assessment_data = AssessmentData.objects.filter(assessmentVersion = assessment)
            assessment_qs.union(assessment_data)
        return assessment_qs
    def get_context_data(self, **kwargs):
        """
        Returns context for the template, including all information relating to data collection

        Returns:
            dict : context for template
        """
        context = super(DataCollectionSummary, self).get_context_data(**kwargs)
        context['toDo'] = todoGetter(3,self.report)
        context['reqTodo'] = len(context['toDo']['r'])
        context['sugTodo'] = len(context['toDo']['s'])
        return section3Context(self,context)

class CreateDataCollectionRow(DeptReportMixin,FormView):
    """
    View to add new data

    Keyword Args:
        assessment (str): primary key of :class:`~makeReports.models.assessment_models.AssessmentVersion` to add data for
    """
    template_name = "makeReports/DataCollection/addDataCollection.html"
    form_class = AddDataCollection
    def dispatch(self, request, *args, **kwargs):
        """
        Dispatches view and attaches :class:`~makeReports.models.assessment_models.AssessmentVersion` to instance

        Args:
            request(HttpRequest): request to view page
            
        Returns:
            HttpResponse : response of page to request
        """
        try:
            self.assessment = AssessmentVersion.objects.get(pk=self.kwargs['assessment'])
        except AssessmentVersion.DoesNotExist:
            raise Http404("Assessment matching URL does not exist.")
        return super(CreateDataCollectionRow,self).dispatch(request,*args,**kwargs)
    def get_context_data(self, **kwargs):
        """
        Returns the context for the template, including the assessment

        Returns:
            dict : context of template
        """
        context = super(CreateDataCollectionRow,self).get_context_data(**kwargs)
        context["assess"] = self.assessment
        return context
    def get_success_url(self):
        """
        Gets URL to go to upon success (data summary)

        Returns:
            str : URL of data summary page (:class:`~makeReports.views.data_collection_views.DataCollectionSummary`)
        """
        return reverse_lazy('makeReports:data-summary', args=[self.report.pk])
    def form_valid(self, form):
        """
        Processes form and creates new AssessmentData object

        Also, attempts to set the aggregate field

        Args:
            form (AddDataCollection): filled out form to be processed
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        assessmentDataObj = AssessmentData.objects.create(
            assessmentVersion=self.assessment, 
            dataRange=form.cleaned_data['dataRange'], 
            numberStudents=form.cleaned_data['numberStudents'], 
            overallProficient=form.cleaned_data['overallProficient']
            )
        assessmentDataObj.save()
        return super(CreateDataCollectionRow, self).form_valid(form)
class CreateDataCollectionRowAssess(CreateDataCollectionRow):
    """
    View to create data collection row from assessment page
    """
    def get_success_url(self):
        """
        Gets URL to go to upon success (assessment summary)

        Returns:
            str : URL of assessment summary page (:class:`~makeReports.views.assessment_views.AssessmentSummary`)
        """
        return reverse_lazy('makeReports:assessment-summary', args=[self.report.pk])

class EditDataCollectionRow(DeptReportMixin,FormView):
    """
    View to edit a data point

    Keyword Args:
        dataCollection (str): primary key of :class:`~makeReports.models.data_models.AssessmentData` to edit
    """
    template_name = "makeReports/DataCollection/editDataCollection.html"
    form_class = AddDataCollection

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatches view and attaches :class:`~makeReports.models.data_models.AssessmentData` to instance

        Args:
            request (HttpRequest): request to view page
            
        Returns:
            HttpResponse : response of page to request
        """
        try:
            self.dataCollection = AssessmentData.objects.get(pk=self.kwargs['dataCollection'])
        except AssessmentData.DoesNotExist:
            raise Http404("Data matching URL does not exist.")
        return super(EditDataCollectionRow,self).dispatch(request,*args,**kwargs)
    def get_context_data(self, **kwargs):
        """
        Gets context for template, including the assessment

        Returns:
            dict : context for template
        """
        context = super(EditDataCollectionRow,self).get_context_data(**kwargs)
        context["assess"] = self.dataCollection.assessmentVersion
        return context
    def get_initial(self):
        """
        Initializes form values based upon current values

        Returns:
            dict : initial form values 
        """
        initial = super(EditDataCollectionRow, self).get_initial()
        initial['dataRange'] = self.dataCollection.dataRange
        initial['numberStudents'] = self.dataCollection.numberStudents
        initial['overallProficient'] = self.dataCollection.overallProficient
        return initial

    def get_success_url(self):
        """
        Gets URL to go to upon success (data summary)

        Returns:
            str : URL of data summary page (:class:`~makeReports.views.data_collection_views.DataCollectionSummary`)
        """
        return reverse_lazy('makeReports:data-summary', args=[self.report.pk])

    def form_valid(self, form):
        """
        Saves data collection object with updated values based upon form

        Args:
            form (AddDataCollection): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        self.dataCollection.dataRange = form.cleaned_data['dataRange']
        self.dataCollection.numberStudents = form.cleaned_data['numberStudents']
        self.dataCollection.overallProficient = form.cleaned_data['overallProficient']
        self.dataCollection.save()
        return super(EditDataCollectionRow, self).form_valid(form)

class DeleteDataCollectionRow(DeptReportMixin,DeleteView):
    """
    View to delete data point

    Keyword Args:
        pk (str): primary key of :class:`~makeReports.models.data_models.AssessmentData` to delete
    """
    model = AssessmentData
    template_name = "makeReports/DataCollection/deleteDataCollection.html"

    def get_success_url(self):
        """
        Gets URL to go to upon success (data summary)

        Returns:
            str : URL of data summary page (:class:`~makeReports.views.data_collection_views.DataCollectionSummary`)
        """
        return reverse_lazy('makeReports:data-summary', args=[self.report.pk])


class NewSLOStatus(DeptReportMixin,FormView):
    """
    Creates a new SLO Status object
    """
    template_name = "makeReports/DataCollection/SLOStatus.html"
    form_class = SLOStatusForm
    
    def dispatch(self, request, *args, **kwargs):
        """
        Attaches the SLO to the instance

        Keyword Args:
            slopk (int): primary key of SLO (:class:`~makeReports.models.slo_models.SLOInReport`) to create status of 
        """
        try:
            self.slo = SLOInReport.objects.get(pk=self.kwargs['slopk'])
        except SLOInReport.DoesNotExist:
            raise Http404("SLO matching URL does not exist.")
        return super(NewSLOStatus,self).dispatch(request,*args,**kwargs)
    def get_context_data(self, **kwargs):
        """
        Gets context for template

        Returns:
            dict : context for template
        """
        context = super(NewSLOStatus,self).get_context_data(**kwargs)
        assessments = AssessmentVersion.objects.filter(slo=self.slo).order_by('number','pk')
        assessTargs = list()
        for a in assessments:
            try:
                agg = AssessmentAggregate.objects.get(assessmentVersion=a)
                assessTargs.append((a.number,a.assessment.title,a.target,agg.aggregate_proficiency))
            except:
                assessTargs.append((a.number,a.assessment.title,a.target,"-"))
        context["aTs"] = assessTargs
        context['slo'] = self.slo
        return context
    def get_success_url(self):
        """
        Gets URL to go to upon success (data summary)

        Returns:
            str : URL of data summary page (:class:`~makeReports.views.data_collection_views.DataCollectionSummary`)
        """
        return reverse_lazy('makeReports:data-summary', args=[self.report.pk])

    def form_valid(self, form):
        """
        Creates the SLO status object

        Args:
            form (SLOStatusForm): completed form to process
        """
        try:
            slo_status_obj = SLOStatus.objects.create(
                status = form.cleaned_data['status'], 
                sloIR=self.slo,
                override = True)
            slo_status_obj.save()
        except:
            pass
        return super(NewSLOStatus, self).form_valid(form)


class EditSLOStatus(DeptReportMixin,FormView):
    """
    View to edit SLO status

    Keyword Args:
        slopk (str): primary key of :class:`~makeReports.models.slo_models.SLO`
        statuspk (str): primary key of :class:`~makeReports.models.data_models.SLOStatus`
    """
    template_name = "makeReports/DataCollection/SLOStatus.html"
    form_class = SLOStatusForm
    
    def dispatch(self, request, *args, **kwargs):
        """
        Dispatches view and attaches :class:`~makeReports.models.slo_models.SLO`, :class:`~makeReports.models.slo_models.SLOInReport`,
         and :class:`~makeReports.models.data_models.SLOStatus` to the instance

        Args:
            request (HttpRequest): request to view page
            
        Returns:
            HttpResponse : response of page to request
        """
        try:
            self.slo = SLOInReport.objects.get(pk=self.kwargs['slopk'])
            self.slo_status = SLOStatus.objects.get(pk=self.kwargs['statuspk'])
        except SLOInReport.DoesNotExist:
            raise Http404("No SLO matches the URL.")
        except SLOStatus.DoesNotExist:
            raise Http404("No status matches the URL")
        return super(EditSLOStatus,self).dispatch(request,*args,**kwargs)

    def get_initial(self):
        """
        Initializes form based upon current value

        Returns:
            dict : initial form values
        """
        initial = super(EditSLOStatus, self).get_initial()
        initial['status'] = self.slo_status.status
        return initial
    def get_context_data(self, **kwargs):
        """
        Gets context for template

        Returns:
            dict : context for template
        """
        context = super(EditSLOStatus,self).get_context_data(**kwargs)
        assessments = AssessmentVersion.objects.filter(slo=self.slo).order_by('number','pk')
        assessTargs = list()
        for a in assessments:
            try:
                agg = AssessmentAggregate.objects.get(assessmentVersion=a)
                assessTargs.append((a.number,a.assessment.title,a.target,agg.aggregate_proficiency))
            except:
                assessTargs.append((a.number,a.assessment.title,a.target,"-"))
        context["aTs"] = assessTargs
        context['slo'] = self.slo
        return context
    def get_success_url(self):
        """
        Gets URL to go to upon success (data summary)

        Returns:
            str : URL of data summary page (:class:`~makeReports.views.data_collection_views.DataCollectionSummary`)
        """
        return reverse_lazy('makeReports:data-summary', args=[self.report.pk])

    def form_valid(self, form):
        """
        Sets SLO status based upon the form

        Args:
            form (SLOStatusForm): filled out form to process
            
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        self.slo_status.status = form.cleaned_data['status']
        self.slo_status.override = True
        self.slo_status.save()
        return super(EditSLOStatus, self).form_valid(form)


class NewResultCommunication(DeptReportMixin,FormView):
    """
    View to create new result communication
    """
    template_name = "makeReports/DataCollection/ResultCommunication.html"
    form_class = ResultCommunicationForm
    def get_success_url(self):
        """
        Gets URL to go to upon success (data summary)

        Returns:
            str : URL of data summary page (:class:`~makeReports.views.data_collection_views.DataCollectionSummary`)
        """
        return reverse_lazy('makeReports:data-summary', args=[self.report.pk])

    def form_valid(self, form):
        """
        Sets SLO status based upon the form

        Args:
            form (SLOStatusForm): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        result_communication = ResultCommunicate.objects.create(
            report = self.report, 
            text = form.cleaned_data['text']
            )
        result_communication.save()
        return super(NewResultCommunication, self).form_valid(form)


class EditResultCommunication(DeptReportMixin,FormView):
    """
    View to edit result communication

    Keyword Args:
        resultpk (str): primary key of :class:`~makeReports.models.data_models.ResultCommunicate` to edit
    """
    template_name = "makeReports/DataCollection/ResultCommunication.html"
    form_class = ResultCommunicationForm
    
    def dispatch(self, request, *args, **kwargs):
        """
        Dispatches view and attaches :class:`~makeReports.models.data_models.ResultCommunicate` to instance

        Args:
            request (HttpRequest): request to view page
            
        Returns:
            HttpResponse : response of page to request
        """
        try:
            self.result_communication = ResultCommunicate.objects.get(pk=self.kwargs['resultpk'])
        except ResultCommunicate.DoesNotExist:
            raise Http404("No result communication matches the URL")
        return super(EditResultCommunication,self).dispatch(request,*args,**kwargs)

    def get_initial(self):
        """
        Returns initial form based upon current values in database

        Returns:
            dict : initial form values
        """
        initial = super(EditResultCommunication, self).get_initial()
        initial['text'] = self.result_communication.text
        return initial
    def get_success_url(self):
        """
        Gets URL to go to upon success (data summary)

        Returns:
            str : URL of data summary page (:class:`~makeReports.views.data_collection_views.DataCollectionSummary`)
        """
        return reverse_lazy('makeReports:data-summary', args=[self.report.pk])

    def form_valid(self, form):
        """
        Sets data communication based upon the form

        Args:
            form (ResultCommunicationForm): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        self.result_communication.report = self.report
        self.result_communication.text = form.cleaned_data['text']
        self.result_communication.save()
        return super(EditResultCommunication, self).form_valid(form)
class Section3Comment(DeptReportMixin,FormView):
    """
    View to add a comment for section 3
    """
    template_name = "makeReports/DataCollection/comment.html"
    form_class = Single2000Textbox
    def get_success_url(self):
        """
        Gets URL to go to upon success (data summary)

        Returns:
            str : URL of data summary page (:class:`~makeReports.views.data_collection_views.DataCollectionSummary`)
        """
        return reverse_lazy('makeReports:data-summary', args=[self.report.pk])
    def form_valid(self, form):
        """
        Sets comment based upon the form

        Args:
            form (Single2000Textbox): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        self.report.section3Comment = form.cleaned_data['text']
        self.report.save()
        return super(Section3Comment,self).form_valid(form)
    def get_initial(self):
        """
        Sets initial form value based upon current value

        Returns:
            dict : initial form values
        """
        initial = super(Section3Comment,self).get_initial()
        initial['text']="No comment."
        if self.report.section3Comment:
            initial['text'] = self.report.section3Comment
        return initial
class DataAssessmentAddInfo(DeptReportMixin,CreateView):
    """
    View to add additional information to data section
    """
    model = DataAdditionalInformation
    fields = ['comment','supplement']
    template_name = "makeReports/DataCollection/addInfo.html"
    def form_valid(self,form):
        """
        Sets report to the current report and then creates object based upon the form
        
        Args:
            form (ModelForm): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        form.instance.report=self.report
        return super(DataAssessmentAddInfo,self).form_valid(form)
    def get_success_url(self):
        """
        Gets URL to go to upon success (data summary)

        Returns:
            str : URL of data summary page (:class:`~makeReports.views.data_collection_views.DataCollectionSummary`)
        """
        return reverse_lazy('makeReports:data-summary', args=[self.report.pk])
class DataAssessmentDeleteInfo(DeptReportMixin,DeleteView):
    """
    View to delete additional data information

    Keyword Args:
        pk (str): primary key of :class:`~makeReports.models.data_models.DataAdditionalInformation` to delete
    """
    model = DataAdditionalInformation
    template_name = "makeReports/DataCollection/deleteInfo.html"
    def get_success_url(self):
        """
        Gets URL to go to upon success (data summary)

        Returns:
            str : URL of data summary page (:class:`~makeReports.views.data_collection_views.DataCollectionSummary`)
        """
        return reverse_lazy('makeReports:data-summary', args=[self.report.pk])
class DataAssessmentUpdateInfo(DeptReportMixin,UpdateView):
    """
    View to update data assessment supplement
    
    Keyword Args:
        pk (str): primary key of :class:`~makeReports.models.data_models.DataAdditionalInformation` to update
    """
    model = DataAdditionalInformation
    template_name = "makeReports/DataCollection/updateInfo.html"
    fields = ['comment']
    def get_success_url(self):
        """
        Gets URL to go to upon success (data summary)

        Returns:
            str : URL of data summary page (:class:`~makeReports.views.data_collection_views.DataCollectionSummary`)
        """
        return reverse_lazy('makeReports:data-summary', args=[self.report.pk])

class AssessmentAggregateCreate(DeptReportMixin, CreateView):
    """
    View to create assessment aggregate
    """
    model = AssessmentAggregate
    form_class = AssessmentAggregateForm
    template_name = "makeReports/DataCollection/addAggregate.html"
    def form_valid(self,form):
        """
        Sets whether the target has been met and then create objects based upon the form
        
        Args:
            form (AssessmentAggregateForm): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        try:
            self.assess = AssessmentVersion.objects.get(pk=self.kwargs['assessment'])
        except AssessmentVersion.DoesNotExist:
            raise Http404("No assessment matching the the URL")
        form.instance.assessmentVersion = self.assess
        if self.assess.target <= form.instance.aggregate_proficiency:
            form.instance.met = True
        else:
            form.instance.met = False
        form.instance.override = True
        return super(AssessmentAggregateCreate,self).form_valid(form)
    def get_success_url(self):
        """
        Gets the success url
        Returns:
            str : URL of data summary (:class:`~makeReports.views.data_collection_views.DataCollectionSummary`)
        """
        return reverse_lazy('makeReports:data-summary', args=[self.report.pk])
class AssessmentAggregateEdit(DeptReportMixin, UpdateView):
    """
    View to edit assessment aggregate

    Keyword Args:
        pk (str): primary key of :class:`~makeReports.models.data_models.AssessmentAggregate` to update
    """
    model = AssessmentAggregate
    form_class = AssessmentAggregateForm
    template_name = "makeReports/DataCollection/addAggregate.html"
    def form_valid(self,form):
        """
        Updates object, including whether the target has been met 

        Args:
            form (AssessmentAggregateForm): filled out form to process
                
        Returns:
            HttpResponseRedirect : redirects to success URL given by get_success_url
        """
        try:
            self.assess = AssessmentVersion.objects.get(pk=self.kwargs['assessment'])
        except AssessmentVersion.DoesNotExist:
            raise Http404("No assessment matching the URL")
        if self.assess.target <= form.instance.aggregate_proficiency:
            form.instance.met = True
        else:
            form.instance.met = False
        form.instance.override = True
        return super(AssessmentAggregateEdit,self).form_valid(form)
    def get_success_url(self):
        """
        Gets the success url 
        Returns:
            str : URL of data summary (:class:`~makeReports.views.data_collection_views.DataCollectionSummary`)
        """
        return reverse_lazy('makeReports:data-summary', args=[self.report.pk])

