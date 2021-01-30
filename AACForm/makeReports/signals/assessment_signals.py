"""
Contains all signals for models relating to Assessment models
"""
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from makeReports.models import (
    AssessmentVersion
)


def post_create_update_assessment_uses(instance):
    """
    After an assessment version is created, increment the number of uses of Assessment by 1

    Args:
        instance (AssessmentVersion): assessment updated
    """
    instance.assessment.numberOfUses += 1
    instance.slo.numberOfAssess += 1
    instance.assessment.save()
    instance.slo.save()

def post_save_update_agg_by_assessment(instance):
    """
    Updates aggregate (AssessmentAggregate) when AssessmentVersion is changed, in case the target value changed
    
    Args:
        instance (AssessmentVersion): assessment updated
    """
    try:
        aa = instance.assessmentaggregate
        if aa and not aa.override:
            met = (aa.aggregate_proficiency >= instance.target)
            if not (met == aa.met):
                aa.met = met
                aa.save()
    except:
        pass

@receiver(post_save,sender=AssessmentVersion)
def post_save_receiver_assessment(sender,instance,created,**kwargs):
    """
    Post save receiver that triggers aggregates and numbers to be updated
    
    Args:
        sender (type): model type sending hook
        instance (AssessmentVersion): assessment updated
        created (bool): whether model was newly created
    """
    post_save_update_agg_by_assessment(instance)
    if created:
        post_create_update_assessment_uses(instance)
    

@receiver(post_delete,sender=AssessmentVersion)
def post_delete_assessment_update_numbering(sender, instance, **kwargs):
    """
    Updates the numbering of assessments in the same report

    Args:
        sender (type): model type sending hook
        instance (AssessmentVersion): assessment deleted
    """
    assessment = instance.assessment
    slo = instance.slo
    oldNum = instance.number
    if assessment.numberOfUses <= 1:
        assessment.delete()
    else:
        assessment.numberOfUses -= 1
        assessment.save()
    assess = AssessmentVersion.objects.filter(report=instance.report,slo=slo)
    for a in assess:
        if a.number > oldNum:
            a.number -= 1
            a.save()
    slo.numberOfAssess -= 1
    slo.save()