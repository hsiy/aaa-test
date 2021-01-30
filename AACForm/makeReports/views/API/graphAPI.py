"""
This file contains the APIs to return graphs
"""
import io
from datetime import datetime, timedelta
from matplotlib.ticker import FuncFormatter
import pandas as pd
import json
import django.core.files as files
from django.http import Http404
from rest_framework import views, status
from rest_framework.response import Response
from makeReports.models import AssessmentAggregate, DegreeProgram, Graph, SLOInReport, SLOStatus
from makeReports.choices import SLO_STATUS_CHOICES

def get_specificSLO_graph(request):
    """
    Graphs a specific SLO/Assessment combination performance over time

    Args:
        request (HttpRequest): contains GET parameters
    Returns:
        matplotlib.figure.Figure : figure, i.e. the graph
    Notes:
        Uses POST data 'report__year__gte' (min year), 'report__year__lte' (max year),
        'report__degreeProgram' (degree program pk), 'sloIR' (SLOInReport primary key),
        'assess' (Assessment primary key)
    """
    begYear=request.data['report__year__gte']
    endYear = request.data['report__year__lte']
    bYear=int(begYear)
    eYear=int(endYear)
    degreeProgram = request.data['report__degreeProgram']
    slo = request.data['sloIR']
    try:
        sloObj = SLOInReport.objects.get(pk=slo)
    except SLOInReport.DoesNotExist:
        raise Http404("SLO matching URL does not exist.")
    assess = request.data['assess']
    queryset = AssessmentAggregate.objects.filter(
        assessmentVersion__assessment__pk = assess,
        assessmentVersion__report__year__gte=begYear,
        assessmentVersion__report__year__lte = endYear,
        assessmentVersion__report__degreeProgram__pk = degreeProgram,
        assessmentVersion__slo__slo = sloObj.slo
        )

    dataFrame = {
        'Year': [],
        'Target': [],
        'Actual': []
    }
    index = []

    for year in range(bYear,eYear+1):
        qYear = queryset.filter(assessmentVersion__report__year=year)
        for assessA in qYear:
            dataFrame['Year'].append(year)
            dataFrame['Target'].append(assessA.assessmentVersion.target/100)
            dataFrame['Actual'].append(assessA.aggregate_proficiency/100)
        index.append(year)
    df = pd.DataFrame(data=dataFrame)
    #lines = df.plot.line()
    lines = df.plot(kind='bar',x='Year',y=['Target','Actual'])
    lines.set(xlabel="Year", ylabel="Percentage")
    lines.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y))) 
    figure = lines.get_figure()
    return figure
def get_numberSLOs_graph(request):
    """
    Generate the figure that graphs number of each SLO status within a degree program

    Args:
        request (HttpRequest): contains the GET parameters
    Returns:
        matplotlib.figure.Figure : figure, i.e. the graph
    Notes:
        Uses POST parameters 'report__year__gte' (min year), 'report__year__lte' (max year),
        'report__degreeProgram' (degree program pk), and sloWeights (weights of SLOs)
    """
    begYear=request.data['report__year__gte']
    endYear = request.data['report__year__lte']
    sloWeights = json.loads(request.data['sloWeights'])
    bYear=int(begYear)
    eYear=int(endYear)
    degreeProgram = request.data['report__degreeProgram']
    queryset = SLOStatus.objects.filter(
        sloIR__report__year__gte = begYear,
        sloIR__report__year__lte = endYear,
        sloIR__report__degreeProgram__pk = degreeProgram
        )
    dataFrame = {
        'Year':[],
        'Met': [],
        'Partially Met': [],
        'Not Met': [],
        'Unknown': []
    }

    for year in range(bYear,eYear+1):
        qYear = queryset.filter(sloIR__report__year=year)
        overall = qYear.count()
        if overall != 0:
            met = 0
            partiallyMet = 0
            notMet = 0
            unknown = 0
            for weightPk in sloWeights.keys():
                met += qYear.filter(
                    status=SLO_STATUS_CHOICES[0][0],
                    sloIR__slo__pk=weightPk).count()*int(sloWeights[weightPk])
                partiallyMet += qYear.filter(
                    status=SLO_STATUS_CHOICES[1][0],
                    sloIR__slo__pk=weightPk).count()*int(sloWeights[weightPk])
                notMet += qYear.filter(
                    status=SLO_STATUS_CHOICES[2][0],
                    sloIR__slo__pk=weightPk).count()*int(sloWeights[weightPk])
                unknown += qYear.filter(
                    status=SLO_STATUS_CHOICES[3][0],
                    sloIR__slo__pk=weightPk).count()*int(sloWeights[weightPk])
            # met = qYear.filter(status=SLO_STATUS_CHOICES[0][0]).count()
            # partiallyMet = qYear.filter(status=SLO_STATUS_CHOICES[1][0]).count()
            # notMet = qYear.filter(status=SLO_STATUS_CHOICES[2][0]).count()
            # unknown = qYear.filter(status=SLO_STATUS_CHOICES[3][0]).count()
            sumWithWeights = met+partiallyMet+notMet+unknown
            metP = met/sumWithWeights
            parP = partiallyMet/sumWithWeights
            notP = notMet/sumWithWeights
            unkP = unknown/sumWithWeights
        else:
            metP = 0
            parP = 0
            notP = 0
            unkP = 0
        dataFrame['Met'].append(metP)
        dataFrame['Partially Met'].append(parP)
        dataFrame['Not Met'].append(notP)
        dataFrame['Unknown'].append(unkP)
        dataFrame['Year'].append(year)
    
    df = pd.DataFrame(dataFrame)
    lines = df.plot(kind='bar',x='Year',y=['Met','Partially Met','Not Met','Unknown'])
    lines.set(xlabel="Year", ylabel="Percentage")
    lines.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y))) 
    #lines = df.plot(kind='line',x='Year',y='Partially Met',ax=ax)
    #lines = df.plot(kind='line',x='Year',y='Not Met',ax=ax)
    #lines = df.plot(kind='line',x='Year',y='Unknown',ax=ax)
    figure = lines.get_figure()
    return figure
def get_degreeProgramSuccess_graph(request):
    """
    Generates graph of percentage of SLOs being met by degree programs within department

    Returns:
        matplotlib.figure.Figure : figure, i.e. the graph
    Notes:
        Uses POST data 'report__year__gte' (min year), 'report__year__lte' (max year),
        'report__degreeProgram__department' (department pk)
    """
    begYear = request.data['report__year__gte']
    endYear = request.data['report__year__lte']
    bYear=int(begYear)
    eYear=int(endYear)
    thisDep = request.data['report__degreeProgram__department']
    queryset = SLOStatus.objects.filter(
        sloIR__report__year__gte=begYear,
        sloIR__report__year__lte = endYear,
        sloIR__report__degreeProgram__department__pk = thisDep
        )
    depQS = DegreeProgram.active_objects.filter(department=thisDep)
    dataFrame = {
        'Year':[]
    }
    for year in range(bYear,eYear+1):
        qYear = queryset.filter(sloIR__report__year=year)
        for d in depQS:
            qDP = qYear.filter(sloIR__report__degreeProgram = d)
            overall = qDP.count()
            if overall != 0:
                met = qDP.filter(status=SLO_STATUS_CHOICES[0][0]).count()
                metP = met/overall
            else:
                metP = 0 
            name = d.name+" ("+d.level+")"
            try:
                dataFrame[name].append(metP)
            except:
                new = {name:[metP]}
                dataFrame.update(new)
        dataFrame['Year'].append(year)
    df = pd.DataFrame(dataFrame)
    yVals = list(dataFrame.keys()).remove('Year')
    lines = df.plot(kind='bar',x='Year',y=yVals)
    lines.set(xlabel="Year", ylabel="Percentage")
    lines.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y))) 
    figure = lines.get_figure()
    return figure
class createGraphAPI(views.APIView):
    """
    JSON API to get url of graph on file server with specified college,
    department, degree program, start and end dates, specific graph choice,
    and maybe SLO to be graphed
    """
    
    def post(self,request,format=None):
        """
        Returns URL to graph on file server upon get request to API

        Args:
            request (HttpRequest): POST request to API
            format (None): format of request (not used here)
        """
        #Start by deleting some old graphs
        graphs = Graph.objects.filter(dateTime__date__lte=datetime.now()-timedelta(minutes=20))
        for g in graphs:
            g.graph.delete(save=False)
            g.delete()
        dec = request.data['decision']
        if dec == '1':
            #specific SLO
            figure = get_specificSLO_graph(request)
        elif dec == '2':
            #Number of SLOs met
            figure = get_numberSLOs_graph(request)
        elif dec == '3':
            #Number of degree programs meeting target
            figure = get_degreeProgramSuccess_graph(request)
        if figure:
            f1 = io.BytesIO()
            figure.savefig(f1, format="png", bbox_inches='tight')
            content_file = files.images.ImageFile(f1)
            graphObj = Graph.objects.create(dateTime=datetime.now())
            graphObj.graph.save("graph-"+str(request.user)+"-"+str(datetime.now())+".png",content_file)
            return Response(graphObj.graph.url)
        else:
            return Response("error",status.HTTP_404_NOT_FOUND)
