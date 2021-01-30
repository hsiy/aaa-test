"""
When models are saved and deleted, signals automatically update fields in other models dependent upon those models.

For example, the fields which track the number of assessments an SLO has are updated by signals.
"""
from .aacAdmin_signals import *
from .assessment_signals import *
from .data_signals import *
from .slo_signals import *