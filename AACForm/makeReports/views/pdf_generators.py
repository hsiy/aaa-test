"""
This file contains views and methods needed to generate PDFs throughout the application
"""
import io
import tempfile
from datetime import datetime
from functools import wraps
from types import SimpleNamespace
from pathlib import Path
from PyPDF2 import PdfFileMerger, PdfFileReader
from weasyprint import HTML, CSS
from urllib.parse import urlparse
from django.conf import settings 
import django.core.files as files
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import resolve_url
from django_weasyprint import WeasyTemplateView
from makeReports.models import (
    Report,
    GradedRubricItem,
    AssessmentSupplement,
    DataAdditionalInformation,
    ReportSupplement,
    Rubric,
    RubricItem
)
from makeReports.views.helperFunctions.section_context import (
    section1Context,
    section2Context,
    section3Context, 
    section4Context
)
from makeReports.views.helperFunctions.mixins import DeptAACMixin

def test_aac_or_dept(self,*args,**kwargs):
    """
    Ensures the user accessing the page is in the AAC or right department
    Keyword Args:
        report (str): primary key of :class:`~makeReports.models.basic_models.Report`
    Returns:
        boolean : whether user passes test
    """
    try:
        report = Report.objects.get(pk=kwargs['report'])
    except Report.DoesNotExist:
        raise Http404("No report matching the URL exists.")
    dept= (report.degreeProgram.department == self.profile.department)
    aac = getattr(self.profile, "aac")
    return dept or aac
def test_aac(self, *args, **kwargs):
    """
    Ensures the user accessing page is in the AAC
    Returns:
        boolean : whether user passes test
    """
    aac = getattr(self.profile, "aac")
    return aac
def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    
    This function is very slightly modified from Django source code in order to allow args and
    kwargs to be passed to the test function
    Args:
        test_func (method) : function that user must return tru
        login_url (str) : URL to login page
        redirect_field_name (str) : field name of where to put redirect URL
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # the following line is the only change with respect to
            # user_passes_test:
            if test_func(request.user, *args, **kwargs):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator
class PDFPreview(TemplateView):
    """
    View to preview a PDF in HTML form, not intended for end-users, but is useful for the development future extensions
    Args:
        report (str): primary key of :class:`~makeReports.models.basic_models.Report`
    """
    template_name = "makeReports/DisplayReport/pdf.html"
    def dispatch(self,request,*args,**kwargs):
        """
        Dispatches view and attaches :class:`~makeReports.models.basic_models.Report` to the view
        Args:
            request (HttpRequest): request to view PDF page
    
        Keyword Args:
            report (str): primary key of :class:`~makeReports.models.basic_models.Report`
                
        Returns:
            HttpResponse : response of page to request
        """
        self.report = Report.objects.get(pk=self.kwargs['report'])
        return super(PDFPreview,self).dispatch(request,*args,**kwargs)
    def get_context_data(self, **kwargs):
        """
        Gets the context for the template, including the rubric and graded rubric items for the report,
        separated by section
        Returns:
            dict : template context
        """
        context = super(PDFPreview,self).get_context_data(**kwargs)
        context['rubric'] = self.report.rubric
        context['rpt'] = self.report
        context = section1Context(self,context)
        context = section2Context(self,context)
        context = section3Context(self,context)
        context = section4Context(self,context)
        return context
class GradedRubricPDFGen(WeasyTemplateView, DeptAACMixin):
    """
    View to generate a graded rubric PDF
    Keyword Args:
        report (str): primary key of :class:`~makeReports.models.basic_models.Report`
    """
    template_name = "makeReports/Grading/feedbackPDF.html"
    pdf_stylesheets =[
        # Change this to suit your css path
        staticfiles_storage.path('css/report.css'),
        staticfiles_storage.path('css/landscape.css'),
        #settings.STATIC_ROOT + '\\css\\bootstrap-print-color.css',
        #settings.BASE_DIR + 'css/main.css',
    ]
    def dispatch(self,request,*args,**kwargs):
        """
        Dispatches view and attaches :class:`~makeReports.models.basic_models.Report` to the view
        Args:
            request (HttpRequest): request to view PDF page
    
        Keyword Args:
            report (str): primary key of :class:`~makeReports.models.basic_models.Report`
                
        Returns:
            HttpResponse : response of page to request
        """
        try:
            self.report = Report.objects.get(pk=self.kwargs['report'])
        except Report.DoesNotExist:
            raise Http404("Report matching the URL does not exist.")
        return super(GradedRubricPDFGen,self).dispatch(request,*args,**kwargs)
    def get_context_data(self, **kwargs):
        """
        Gets the context for the template, including the rubric and graded rubric items for the report,
        separated by section
        Returns:
            dict : template context
        """
        context = super(GradedRubricPDFGen,self).get_context_data(**kwargs)
        context['rubric'] = self.report.rubric
        context['GRIs1'] = GradedRubricItem.objects.filter(rubric=self.report.rubric, item__section=1).order_by("item__order","item__pk")
        context['GRIs2'] = GradedRubricItem.objects.filter(rubric=self.report.rubric, item__section=2).order_by("item__order","item__pk")
        context['GRIs3'] = GradedRubricItem.objects.filter(rubric=self.report.rubric, item__section=3).order_by("item__order","item__pk")
        context['GRIs4'] = GradedRubricItem.objects.filter(rubric=self.report.rubric, item__section=4).order_by("item__order","item__pk")
        return context
class ReportPDFGen(WeasyTemplateView, DeptAACMixin):
    """
    View to generate PDF of report, without supplements
    Keyword Args:
        report (str): primary key of :class:`~makeReports.models.basic_models.Report`
    """
    template_name = "makeReports/DisplayReport/pdf.html"
    pdf_stylesheets =[
        staticfiles_storage.path('css/report.css'),
        staticfiles_storage.path('css/shelves.css'),
    ]
    def dispatch(self,request,*args,**kwargs):
        """
        Dispatches view and attaches :class:`~makeReports.models.basic_models.Report` to instance
        Args:
            request (HttpRequest): request to view page
        
        Keyword Args:
            report (str): primary key of :class:`~makeReports.models.basic_models.Report`
        Returns:
            HttpResponse : response of page to request
        """
        try:
            self.report = Report.objects.get(pk=self.kwargs['report'])
        except Report.DoesNotExist:
            raise Http404("Report matching URL does not exist.")
        return super(ReportPDFGen,self).dispatch(request,*args,**kwargs)
    def get_context_data(self, **kwargs):
        """
        Gets the context for the template, including the report and context
        needed for each section
        Returns:
            dict : context for template
        """
        context = super(ReportPDFGen,self).get_context_data(**kwargs)
        context['rubric'] = self.report.rubric
        context['rpt'] = self.report
        context = section1Context(self,context)
        context = section2Context(self,context)
        context = section3Context(self,context)
        context = section4Context(self,context)
        return context
def addSupplements(sups,merged):
    """
    Adds supplements to the merged PDF

    Args:
        sups : QuerySet of supplements to merge
        merged: PdfFileMerger to add to
    Returns:
        PdfFileMerger : with supplements integrated
    """
    fSup = tempfile.TemporaryFile()
    nonPdfs = []
    for sup in sups:
        if Path(sup.supplement.name).suffix[1:].lower() == "pdf":
            merged.append(PdfFileReader(sup.supplement.open()))
        else:
            nonPdfs.append((sup.supplement.name,sup.supplement.url))
    if len(nonPdfs)>0:
        secSups = get_template('makeReports/DisplayReport/PDFsub/extraSups.html')
        pSups = secSups.render({"urls":nonPdfs}).encode()
        htmlSup = HTML(string = pSups)
        htmlSup.write_pdf(target=fSup,stylesheets=[CSS(staticfiles_storage.path('css/report.css'))])
        merged.append(fSup)
    return merged
@login_required
@user_passes_test(test_aac_or_dept)
def reportPDF(request, report):
    """
    View to generate report PDF with supplements
    Args:
        request (HttpRequest): request to view page
        report (str): primary key of :class:`~makeReports.models.basic_models.Report` 
    Returns:
        HttpResponse : the PDF
    Notes:
        A function instead of class due to limitations of class based views
    """
    #first get report or return 404 error
    report = get_object_or_404(Report, pk=report)
    #get templates for each of the sections (sec 1 and 2 together since sec 1 doesn't have supplements) 
    sec1and2 = get_template('makeReports/DisplayReport/PDFsub/pdf1and2.html')
    sec3 = get_template('makeReports/DisplayReport/PDFsub/pdf3.html')
    sec4 = get_template('makeReports/DisplayReport/PDFsub/pdf4.html')
    #build the context needed for the report
    context = {'rpt':report, 'report':report}
    #SimpleNamespace lets report be accessed via dot-notation in section#Context
    s = SimpleNamespace(**context)
    context = section1Context(s,context)
    context = section2Context(s,context)
    #render HTML string for section 1 and 2
    p1and2 = sec1and2.render(context).encode()
    #reset context for section 3
    context = {'rpt':report, 'report':report}
    context = section3Context(s,context)
    #render HTML string for section 3
    p3 = sec3.render(context).encode()
    #reset context
    context = {'rpt':report, 'report':report}
    context = section4Context(s,context)
    #render HTML string for section 4
    p4 =sec4.render(context).encode()
    #get all supplements (PDFs) that go with the report
    assessSups = AssessmentSupplement.objects.filter(assessmentversion__report=report)
    dataSups = DataAdditionalInformation.objects.filter(report=report)
    repSups = ReportSupplement.objects.filter(report=report)
    #get the HTML of all sections
    html1and2 = HTML(string=p1and2)
    html3 = HTML(string=p3)
    html4 = HTML(string=p4)
    #set-up temporary files to write pdfs for each section
    f1and2 = tempfile.TemporaryFile()
    f3 = tempfile.TemporaryFile()
    f4 = tempfile.TemporaryFile()
    #write to those temporary files from the HTML generated
    html1and2.write_pdf(target=f1and2,stylesheets=[CSS(staticfiles_storage.path('css/report.css'))])
    html3.write_pdf(target=f3,stylesheets=[CSS(staticfiles_storage.path('css/report.css')),CSS(staticfiles_storage.path('css/shelves.css'))])
    html4.write_pdf(target=f4,stylesheets=[CSS(staticfiles_storage.path('css/report.css'))]) 
    #set-up a merger to merge all PDFs together
    merged = PdfFileMerger()
    merged.append(f1and2)
    #start with section 1 and 2, then append assessment supplements
    merged = addSupplements(assessSups, merged)
    #add section 3
    merged.append(f3)
    #append data supplements
    merged = addSupplements(dataSups, merged)
    #append section 4
    merged.append(f4)
    #add report supplements
    merged = addSupplements(repSups, merged)
    #write the merged pdf to the HTTP Response
    http_response = HttpResponse(content_type="application/pdf")
    merged.write(http_response)
    return http_response
@login_required
@user_passes_test(test_aac)
def UngradedRubric(request, rubric):
    """
    View to generate ungraded rubric PDF
    Args:
        request (HttpRequest): request for page
        rubric (str): primary key of :class:`~makeReports.models.grading_models.Rubric`
    Returns:
        HttpResponse : the PDF
    """
    rubric = get_object_or_404(Rubric, pk=rubric)
    template = get_template("makeReports/Grading/rubricPDF.html")
    context = dict()
    context['rubric'] = rubric
    #get the rubric items separated by section
    context['RIs1'] = RubricItem.objects.filter(rubricVersion=rubric, section=1)
    context['RIs2'] = RubricItem.objects.filter(rubricVersion=rubric, section=2)
    context['RIs3'] = RubricItem.objects.filter(rubricVersion=rubric, section=3)
    context['RIs4'] = RubricItem.objects.filter(rubricVersion=rubric, section=4)
    rend = template.render(context).encode()
    html = HTML(string=rend)
    f1 = io.BytesIO()
    html.write_pdf(target=f1,stylesheets=[CSS(staticfiles_storage.path('css/report.css')),CSS(staticfiles_storage.path('css/landscape.css'))])
    content_file = files.File(f1)
    try:
        rubric.fullFile.delete()
    except:
        pass
    rubric.fullFile.save(rubric.name+"-"+str(datetime.now())+".pdf",content_file)
    rubric.save()
    http_response = HttpResponseRedirect(rubric.fullFile.url)
    return http_response