"""
Contains all signals relating to data collection models
"""
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from makeReports.models import (
    AssessmentAggregate,
    AssessmentData,
    SLOStatus
)
from makeReports.choices import SLO_STATUS_CHOICES


@receiver(post_save,sender=AssessmentData)
def post_save_agg_by_data(sender, instance, **kwargs):
    """
    Updates aggregates when data is created or modified post-save
    
    Args:
        sender (type): model type sending hook
        instance (AssessmentData): data updated
    """
    update_agg_by_data(sender,instance, 0)
@receiver(pre_delete,sender=AssessmentData)
def pre_delete_agg_by_data(sender,instance,**kwargs):
    """
    Updates aggregates when data is deleted
    
    Args:
        sender (type): model type sending hook
        instance (AssessmentData): data updated
    """
    update_agg_by_data(sender,instance, 1)
def update_agg_by_data(sender, instance, sigType):
    """
    Updates the assessment aggregate when data is modified or created and it has not been previously overridden
    
    Args:
        sender (type): model type sending hook
        instance (AssessmentData): data updated
        sigType (int): signal type - 0 if save, 1 if delete
    """
    try:
        update_agg(instance.assessmentVersion.assessmentaggregate,sigType,instance.pk, instance.assessmentVersion)
    except:
        update_agg(None,sigType,instance.pk,instance.assessmentVersion)

def update_agg(agg, sigType, pk, assessment):
    """
    Updates an assessment aggregate that has not been previously overriden

    Args:
        agg (AssessmentAggregate): aggregate to update
        sigType (int): signal type - 0 if save, 1 if delete
        pk (int): primary key of instance that changed (only needed if pre-delete)
        assessment (AssessmentVersion): assessment of aggregate
    """
    if agg:
        if not agg.override:
            agg.aggregate_proficiency = calcWeightedAgg(assessment, sigType, pk)
            agg.met = (agg.aggregate_proficiency >= assessment.target)
            agg.save()
    else:
        aProf = calcWeightedAgg(assessment, sigType, pk)
        met = (aProf >= assessment.target)
        AssessmentAggregate.objects.create(
            assessmentVersion=assessment,
            aggregate_proficiency=aProf, 
            met = met)

def calcWeightedAgg(assessment, sigType, pk):
    """
    Calculates the weighted aggregate value based upon assessment data for 
    the given :class:`~makeReports.models.assessment_models.AssessmentVersion`

    Args:
        assessment (~makeReports.models.assessment_models.AssessmentVersion) : the assessment to calculate the aggregate for
        sigType (int): signal type - 0 is post-save, 1 is pre-delete
        pk (int): primary key of instance that changed (only needed if pre-delete)

    Returns:
        int : the weighted aggregate
    """
    data = AssessmentData.objects.filter(assessmentVersion=assessment)
    if sigType == 1:
        data = data.exclude(pk=pk)
    totalStudents = 0
    totalProf = 0
    for dat in data:
        totalStudents += dat.numberStudents
        totalProf += dat.numberStudents*dat.overallProficient
    if totalStudents==0:
        return 0
    return round(totalProf/totalStudents)

@receiver(post_save,sender=AssessmentAggregate)
def post_save_status_by_agg(sender,instance,**kwargs):
    """
    Updates status based upon aggregates after model is saved

    Args:
        sender (type): model type sending hook
        instance (AssessmentAggregate): data updated
    """
    update_status_by_agg(sender,instance, 0)
@receiver(pre_delete,sender=AssessmentAggregate)
def pre_delete_status_by_agg(sender,instance,**kwargs):
    """
    Updates status based upon aggregates after model is saved

    Args:
        sender (type): model type sending hook
        instance (AssessmentAggregate): data updated
    """
    update_status_by_agg(sender,instance,1)

def update_status_by_agg(sender, instance, sigType):
    """
    Updates the SLO status based upon aggregate when aggregates are created or modified
    
    Args:
        sender (type): model type sending hook
        instance (AssessmentAggregate): data updated
        sigType (int): signal type - 0 is post-save, 1 if pre-delete
    """
    sloIR = instance.assessmentVersion.slo
    try:
        sS = SLOStatus.objects.get(sloIR=sloIR)
        override = sS.override
    except:
        sS = None
        override = False
    if not override:
        update_status(sS,sigType,instance.pk, sloIR)

def update_status(sS, sigType, pk, sloIR):
    """
    Updates the status based upon the AssessmentAggregate values for a given status

    Args:
        sS (SLOStatus): SLO status to update
        sigType (int): signal type - 0 is post-save, 1 if pre-delete
        pk (int): primary key of AssessmentAggregate to exclude if sigType is 1
        sloIR (SLOInReport): the SLO to update the status of
    """
    aggs = AssessmentAggregate.objects.filter(assessmentVersion__slo=sloIR)
    if sigType==1:
        aggs = aggs.exclude(pk=pk)
    met = True
    partiallyMet = False
    for a in aggs:
        if a.met is False:
            met = False
        if a.met is True:
            partiallyMet=True
        if not met and partiallyMet:
            break
    if sS:
        if met:
            sS.status = SLO_STATUS_CHOICES[0][0]
        elif partiallyMet:
            sS.status = SLO_STATUS_CHOICES[1][0]
        else:
            sS.status = SLO_STATUS_CHOICES[2][0]
        sS.save()
    else:
        if met:
            SLOStatus.objects.create(status=SLO_STATUS_CHOICES[0][0],sloIR=sloIR)
        elif partiallyMet:
            SLOStatus.objects.create(status=SLO_STATUS_CHOICES[1][0],sloIR=sloIR)
        else:
            SLOStatus.objects.create(status=SLO_STATUS_CHOICES[2][0],sloIR=sloIR)
