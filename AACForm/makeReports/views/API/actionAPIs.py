"""
This file contains the APIs the front-end call to trigger an action on the back-end
"""
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from makeReports.models import AssessmentAggregate, Report, SLOStatus
from makeReports.signals import update_status, update_agg

class ClearOverrideAPI(APIView):
    """
    Clears the overriden aggregates and SLO statuses
    """
    renderer_classes = [JSONRenderer]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request,format=None):
        """
        Clears the overridden aggregates and SLO statuses for given report

        Args:
            request (HttpRequest): the request to the API
            format (None): not used
        Returns:
            response (Response): empty response

        Notes:
            Expects primary key of report to be passed in GET request as 'pk'
        """
        pk = int(request.query_params['pk'])
        try:
            rpt = Report.objects.get(pk=pk)
        except Report.DoesNotExist:
            raise Http404("Report matching URL does not exist")
        if((rpt.degreeProgram.department==request.user.profile.department) or request.user.profile.aac):
            #only proceed if the person truly has the right to modify the report
            aggs = AssessmentAggregate.objects.filter(assessmentVersion__report__pk=pk, override=True)
            for agg in aggs:
                agg.override = False
                #update_agg will save the change
                update_agg(agg,0,0,agg.assessmentVersion)
            statuses = SLOStatus.objects.filter(sloIR__report__pk=pk, override=True)
            for status in statuses:
                status.override = False
                #update_status will save the change
                update_status(status,0,0, status.sloIR)
            return Response()

