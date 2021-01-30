"""
This file contains the APIs which return JSON to the front-end
"""
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Subquery
from makeReports.models import (
    AssessmentVersion, 
    Department, 
    DegreeProgram, 
    Report, 
    SLOInReport
)
from makeReports.views.helperFunctions import text_processing
from .serializers import (
    AssessmentSerializer,
    DeptSerializer,
    ProgSerializer,
    SLOSerializerWithParent
)


class DeptByColListAPI(generics.ListAPIView):
    """
    JSON API to gets active departments within specified college

    Notes:
        'college' is GET parameter to filter college primary key
    """
    queryset = Department.active_objects.all().order_by("name")
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = (['college'])
    serializer_class = DeptSerializer
class ProgByDeptListAPI(generics.ListAPIView):
    """
    JSON API to gets active degree programs within specified department

    Notes:
        'department' is GET parameter to filter by department primary key
    """
    queryset = DegreeProgram.active_objects.all().order_by("name")
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = (['department'])
    serializer_class = ProgSerializer
class SloByDPListAPI(generics.ListAPIView):
    """
    JSON API to gets past SLOs :class:`~makeReports.models.slo_models.SLO` within specified degree program
    
    Notes:
        'report__degreeProgram' (degreeProgram primary key), 'report__year__gte' (min year),
        'report__year__lte' (max year) are the GET request parameters
    """
    queryset = SLOInReport.objects.all()
    #Gets the most recent SLOInReport for each SLO
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = {'report__degreeProgram':['exact'],
    'report__year':['gte','lte'],
    }
    serializer_class = SLOSerializerWithParent
    def get_queryset(self):
        """
        Gets the filtered QuerySet, and picks the most recent SLOInReport for each parent SLO

        Returns:
            QuerySet : QuerySet of SLOs (:class:`~makeReports.models.slo_models.SLOInReport`) that match parameters
        Notes:
            .order_by(...).distinct(...) is only supported by PostgreSQL
        """
        qS = super(SloByDPListAPI,self).get_queryset()
        qS = qS.order_by('slo','-report__year').distinct('slo')
        #Only 1 order_by per Queryset, but distinct necessitates the first order_by
        #The explicit subqery provides a workaround
        oQS = SLOInReport.objects.all().filter(
            pk__in = Subquery(qS.values("pk"))
        ).order_by("goalText")
        return oQS
class AssessmentBySLO(generics.ListAPIView):
    """
    Filters AssessmentVersion to get the most recent assessment version for each parent assessment

    Notes:
        'slo__slo' (parent SLO pk), 'report__year__gte' (min year), 'report__year__lte' (max year)
        are the GET parameters
    """
    #queryset = AssessmentVersion.objects.order_by('assessment','-report__year').distinct('assessment')
    queryset = AssessmentVersion.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = {
        'slo__slo':['exact'],
        'report__year':['gte','lte'],
    }
    serializer_class = AssessmentSerializer
    def get_queryset(self):
        """
        Gets the filtered queryset, and picks the most recent AssessmentVersion for each parent Assessment

        Returns:
            QuerySet : queryset of assessments that match parameters
        Notes:
            .order_by(...).distinct(...) is only supported by PostgreSQL
        """
        qS = AssessmentVersion.objects.filter(
            pk__in = Subquery(
                super().get_queryset(

                ).order_by(
                    'assessment',
                    '-report__year'
                ).distinct('assessment').values("pk")
            )
        ).order_by("assessment__title")
        return qS
class ImportYearsAPI(APIView):
    """
    Generates list of years a degree program submitted a report
    """
    renderer_classes = [JSONRenderer]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request,format=None):
        """
        Returns years in reverse chronological order where degree program submitted a report

        Args:
            request (HttpRequest): the request to the API
            format (None): not used
        Returns:
            list : list of years formatted in JSON
        Notes:
            Expects 'pk' GET parameter, that is the primary key of the degree program of interest
        """
        pk = int(request.query_params['pk'])
        if pk>=0:
            years = Report.objects.filter(
                degreeProgram__pk=pk
                ).order_by("-year").distinct('year').values('year')
        else:
            years = Report.objects.filter(
                degreeProgram__department=request.user.profile.department
                ).order_by("-year").distinct('year').values('year')
        yearsFormatted = []
        for year in years:
            yearsFormatted.append({
                "value": year["year"],
                "label": str(int(year["year"])-1)+"-"+str(year["year"])
            })
        return Response(yearsFormatted)

class SLOSuggestionsAPI(APIView):
    """
    Generates suggestions for SLOs based upon goal text
    """
    renderer_classes = [JSONRenderer]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        """
        When API is posted to return dictonary of suggestions

        Args:
            request (HttpRequest): request to API
            format (None): not used

        Returns:
            dict : dictionary of suggestions relating to SLO
        """
        slo_text = request.data['slo_text']
        response = text_processing.create_suggestions_dict(slo_text)
        return(Response(response))
class BloomsSuggestionsAPI(APIView):
    """
    Returns suggested words based upon Bloom's level
    """
    renderer_classes = [JSONRenderer]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        """
        When API is posted to return dictonary of suggestions

        Args:
            request (HttpRequest): request to API
            format (None): not used

        Returns:
            dict : dictionary of suggestions relating to SLO
        """
        level = request.data['level']
        response = text_processing.blooms_words(level)
        return(Response(response))

