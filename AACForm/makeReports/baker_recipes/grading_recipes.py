"""
This file contains recipes to create grading models

Attributes:
    gradedRubric (Recipe): recipe to create :class:`~makeReports.grading_models.GradedRubric` model
    rubricItem (Recipe): recipe to create :class:`~makeReports.grading_models.RubricItem` model
    gradedRubricItem (Recipe): recipe to create :class:`~makeReports.grading_models.GradedRubricItem` model
"""
from itertools import cycle
from model_bakery.recipe import Recipe, foreign_key
from makeReports.models.grading_models import RubricItem, GradedRubric, GradedRubricItem

comments = [
    "•	There is evidence of wide-spread faculty involvement that informs and drives continuous program improvement.",
    "•	Evidence of past program improvement decisions and actions appear to have made an impact.",
    "•	The review of SLOs and associated data is a routine and program improvement appears to be an on-going process.  Program improvement efforts are informed by a fully operationalized assessment plan. \
    •	Progress from the previous report is noted.",
    "•	The program has taken action to ensure SLOs and measures represent the relevancy and appropriate rigor graduates will need to be successful after completing the program.",
   " •	The program is commended engaging external stakeholders (alumni/employers/students/community members) in the assessment process. ",
   "•	SLOs are readily accessible to stakeholders outside of the campus.",
   "•	SLOs are incorporated into recruitment and marketing materials.",
   "•	Program curriculum is clearly mapped to the SLOs.\
    •	SLOs and detailed rubrics provide clear and consistent learning targets for students and faculty. \
    •	Assessment informs teaching and learning at the course and program-level. ",
    "•	The program has integrated assessments in a way that provides feedback to the program as a whole and at the same time provides meaningful feedback to individual faculty members and students. "
]

gradedRubric = Recipe(GradedRubric,
    section1Comment = cycle(comments),
    section2Comment = cycle(comments),
    section3Comment = cycle(comments),
    section4Comment = cycle(comments),
    generalComment = cycle(comments)
)

rIs = [
    "Studnet learning outcomes consist of a single construct.",
    "Sutdnet learning outcomes are observable",
    "Student learning outcomes represent discipline-specific context.",
    "Internal and external stakeholders are engaged with student learning outcomes.",
    "Each student learning outcome has at least one direct measure.",
    "Data are regularly collected against the measures.",
    "Data are regularly analyzed against the measures (at least anually)",
    "Results are communicated within the program",
    "Evidence of data-informed decisions is evident."
]
DNMs = [
    "SLOS incluce more than a single,independent construct",
    "SLOs are not obserable and not sufficiently defined to allow for observation",
    "SLOs are not presented in a discipline-specific context",
    "The program has limited or no systematic means to communicate SLOs or engage",
    "Measures provide data that does not reflect the constructs represented in the SLOs"
]

MCs = [
    "Some SLOS include more than a single independent construct.",
    "SLOs are gnerally observable but clarity is needed.",
    "Some SLOS are measured by direct evidence of student knowledge of skill  and other by indirect means",
    "Some measures provide data that reflect the constructs",
    "Results are sporadically communicated to program faculty"
]
MEs = [
    "Specific examples of data-informed decisions are provided",
    "Specific porgram-imporvement actions have been initiated",
    "Data analysis is routine. Plans for systems is optimized.",
    "All measure provide data that reflect the constructs in the SLOs",
    "SLOs are presented in the context of the discipline.",
    "Alls SLOs are observable and sufficient to allow for observation and judgements."
]

abbrevs = ["MO","NS","SA","STA","LS","PR","TQ"]

rubricItem = Recipe(RubricItem,
    text = cycle(rIs),
    abbreviation = cycle(abbrevs),
    DMEtext = cycle(DNMs),
    MEtext = cycle(MCs),
    EEtext = cycle(MEs)
)

gradedRubricItem = Recipe(GradedRubricItem,
    item = foreign_key(rubricItem)
)