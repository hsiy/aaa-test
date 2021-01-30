"""
This file contains recipes to create SLO models

Attributes:
    sloInReport (Recipe): recipe to create :class:`~makeReports.models.slo_models.SLOInReport` model
    gradGoal (Recipe): recipe to create :class:`~makeReports.models.slo_models.GradGoal` model
    slosToStakeholders (Recipe): recipe to create :class:`~makeReports.models.slo_models.SLOsToStakeholders` model
"""
from itertools import cycle
from model_bakery.recipe import Recipe, foreign_key
from makeReports.models.slo_models import GradGoal, SLOInReport, SLOsToStakeholder
from .basic_recipes import report


slos = [
    "Analyze fundamental interdisciplinary evidence-based knowledge and theories for competent gerontological practice",
    "Critique and analyze diverse and complex aging issues and outcomes from an interdisciplinary perspective.",
    "Exhibit abilities to effectively use basic communication (written, oral, interpersonal) skills and information technology.",
    "Evaluate and appraise ability of oneself and others to demonstrate social and cultural awareness, sensitivity, respect, and support of multiple perspectives, and exhibit personal and social responsibility, and ethical and professional behavior in all settings."
    ]

sloInReport = Recipe(SLOInReport,
    goalText = cycle(slos),
    report = foreign_key(report)
)

GGs = [
    "Mastery of discipline content",
    "Proficiency in analyzing, evaluating and synthesizing information",
    "Effective oral and written communication",
    "Knowledge of discipline's ethics and standars"
]

gradGoal = Recipe(GradGoal,
    text = cycle(GGs)
)

stks = [
    "In regard to our SLOs, all facaulty and member of our External Advisory Board (EAB) are aware of our SLOs. We plan to put our SLOs on our program website so that they are publically available. \
    Results are relayed to the unit at least once per year in a departmental faculty meeting where discussion revolves around how to better assess and achieve the various SLOs.\
        Our assessment report will be relayed to our instructors yearly. Further, once each semester our External Advisory Board (EAB) meets. We will ensure that assessment is part of our conversation with them at least once per academic year, twice if necessary. We got feedback from our EAB regarding our SLOs, and will be relaying the results of this report to them this January (2018).",
    "An annual meeting is held every May. The department chair explains the goals this year. Faculty members are consulted.",
    "Results are analyzed by the department head and initial results are sent in an email. Members can ask questions. If sufficient interest, a town-hall style event is held."
]

slosToStakeholder = Recipe(SLOsToStakeholder,
    text = cycle(stks),
    report = foreign_key(report)
)