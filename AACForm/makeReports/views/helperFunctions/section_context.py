"""
This file contains methods that generate the context needed to display each section of the report and grading views.
"""
from makeReports.models import (
    Assessment,
    AssessmentAggregate,
    AssessmentData,
    AssessmentVersion,
    DataAdditionalInformation,
    DecisionsActions,
    ResultCommunicate,
    SLOInReport,
    SLOStatus,
    SLOsToStakeholder
)

def rubricItemsHelper(self,context):
    """
    Adds the text of each rubric item to the context

    Args:
        context (dict): template context
    Returns:
        dict : template context
    """
    extraHelp = dict()
    for rI in self.rubricItems:
        extraHelp["rI"+str(rI.pk)] = [rI.DMEtext, rI.MEtext, rI.EEtext]
    context['extraHelp']=extraHelp
    return context
def section1Context(self,context):
    """
    Adds all context needed to display section 1 of the report (SLOs and stakeholder communication)

    Args:
        context (dict): template context
    Returns:
        dict : template context
    """
    context['slo_list'] = SLOInReport.objects.filter(report=self.report).order_by("number")
    context['stk'] = SLOsToStakeholder.objects.filter(report=self.report).last()
    return context
def section2Context(self,context):
    """
    Adds all context needed to display section 2 of the report (assessments)

    Args:
        context (dict): template context
    Returns:
        dict : template context
    """
    context['assessment_list'] = AssessmentVersion.objects.filter(report=self.report).order_by("slo__number","number")
    return context
def section3Context(self,context):
    """
    Adds all context needed to display section 3 of the report (assessment, SLOs, data points)

    Args:
        context (dict): template context
    Returns:
        dict : template context
    """
    assessment_data_dict = {'useaccform':False, 'assessments':[], 'slo_statuses':[]}
    if self.report.accredited:
        assessment_data_dict['useaccform'] = True
    assessments = AssessmentVersion.objects.filter(report=self.report).order_by("slo__number","number")
    for assessment in assessments:
        temp_dict = dict()
        temp_dict['assessment_id'] = assessment.pk
        try:
            assessment_obj = Assessment.objects.get(pk=assessment.assessment.pk)
            temp_dict['assessment_text'] = assessment_obj.title
            temp_dict['assessment_obj'] = assessment
        except:
            temp_dict['assessment_text'] = None
            temp_dict['assessment_obj'] = None

        try:
            slo_obj = SLOInReport.objects.get(pk=assessment.slo.pk)
            temp_dict['slo_text'] = slo_obj.goalText
            temp_dict['slo_obj'] = slo_obj
        except:
            temp_dict['slo_text'] = None
            temp_dict['slo_obj'] = None

        try:
            assessment_data_objs = AssessmentData.objects.filter(assessmentVersion=assessment)
            temp_dict['assess_data'] = assessment_data_objs
            #temp_dict['num_students_assessed'] = assessment_data_obj.numberStudents
            #temp_dict['overall_proficient'] = assessment_data_obj.overallProficient
            #temp_dict['data_range'] = assessment_data_obj.dataRange
            #temp_dict['assessment_data_id'] = assessment_data_obj.pk
        except:
            temp_dict['assess_data'] = None
            #temp_dict['num_students_assessed'] = None
           # temp_dict['overall_proficient'] = None
            #temp_dict['data_range'] = None
            #temp_dict['assessment_data_id'] = None
        try:
            aggregate = AssessmentAggregate.objects.get(assessmentVersion=assessment)
            temp_dict['agg'] = aggregate
        except:
            temp_dict['agg'] = None

        assessment_data_dict['assessments'].append(temp_dict)

    SLOs = SLOInReport.objects.filter(report=self.report).order_by("number")
    for sloir in SLOs:
        temp_dict = dict()
        temp_dict['slo_obj'] = sloir
        temp_dict['slo_text'] = sloir.goalText
        temp_dict['slo_pk'] = sloir.pk
        try:
            slo_status_obj = SLOStatus.objects.get(sloIR=sloir)
            temp_dict['slo_status'] = slo_status_obj.status
            temp_dict['slo_status_ovr'] = slo_status_obj.override
            temp_dict['slo_status_pk'] = slo_status_obj.pk
        except:
            temp_dict['slo_status'] = None
            temp_dict['slo_status_pk'] = None

        assessment_data_dict['slo_statuses'].append(temp_dict)
        
    try:
        result_communicate_obj = ResultCommunicate.objects.get(report=self.report)
        assessment_data_dict['result_communication_id'] = result_communicate_obj.pk
        assessment_data_dict['result_communication_text'] = result_communicate_obj.text
    except:
        pass
    context['assessment_data_dict'] = assessment_data_dict
    context['supplement_list'] = DataAdditionalInformation.objects.filter(report=self.report)
    return context
def section4Context(self,context):
    """
    Adds all context needed to display section 4 of the report (SLOs and decisions/actions)

    Args:
        context (dict): template context
    Returns:
        dict : template context
    """
    SLOs_ir = SLOInReport.objects.filter(report=self.report).order_by("number")
    context_list = []
    for slo_ir in SLOs_ir:
        temp_dict = dict()
        temp_dict['slo_obj'] = slo_ir
        temp_dict['slo_pk'] = slo_ir.pk
        temp_dict['slo_text'] = slo_ir.goalText
        try:
            decisions_obj = DecisionsActions.objects.get(sloIR=slo_ir)
            temp_dict['decisions_obj'] = decisions_obj
        except:
            temp_dict['decisions_obj'] = None

        context_list.append(temp_dict)
            
    context['decisions_actions_list'] = context_list
    return context
