"""
Contains all signals related to SLO models
"""
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from makeReports.models import (
    SLOInReport
)

@receiver(post_save,sender=SLOInReport)
def post_save_slo_update_numbering(sender,instance,created,**kwargs):
    """
    Post save receiver that triggers numbers to be updated

    Args:
        sender (type): model type sending hook
        instance (SLOInReport): SLO updated
        created (bool): whether model was newly created
    """
    if created:
        instance.report.numberOfSLOs +=1
        instance.report.save()
        instance.slo.numberOfUses += 1
        instance.slo.save()

@receiver(post_delete,sender=SLOInReport)
def post_delete_slo_update_numbering(sender,instance,**kwargs):
    """
    Updates the numbering of SLOs in the same report

    Args:
        sender (type): model type sending hook
        instance (SLOInReport): SLO deleted
    """
    oldNum = instance.number
    if instance.slo.numberOfUses <= 1:
        instance.slo.delete()
    else:
        instance.slo.numberOfUses -= 1
        instance.slo.save()
    slos = SLOInReport.objects.filter(report=instance.report).order_by("number")
    for slo in slos:
        if slo.number > oldNum:
            slo.number -= 1
            slo.save()
    instance.report.numberOfSLOs -= 1
    instance.report.save()