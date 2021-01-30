"""
This file contains recipes to create assessment models

Attributes:
    assessment (Recipe): recipe to create :class:`~makeReports.models.assessment_models.Assessment` model
    assessmentVersion (Recipe): recipe to create :class:`~makeReports.models.assessment_models.AssessmentVersion` model
"""
from itertools import cycle
from model_bakery.recipe import Recipe, foreign_key
from makeReports.models.assessment_models import Assessment, AssessmentVersion
from .basic_recipes import report
from .slo_recipes import sloInReport

titles = ["Final Paper", "Comprehensive Exam", "Project and Presentation in CSCI 4200","Capstone Project","Analytical Paper and Poster","Team Final Project"]

assessment = Recipe(Assessment,
    title = cycle(titles)
)

descriptions = [
    "The students will write an analytic paper examining several different cultures.","The students will prepare a poster outlining a project in statistics. This will be presented to the the board.",
    "The students will take an exam that draws from all classes they have ever taken.","The students will write several essays demonstrating rhetorical analysis.","The students will work as a team to create a project for a client.",
    "The students will present original research in front of a board. They will be asked questions.","The students will each create a statistical model.","The student will perform a series of experiments and write-up the results."
]

wheres = [
    "During ENGL 4050",
    "As part of the capstone class",
    "On a specified day during the last semester",
    "When the students take CSCI 4600",
    "The students individually turn in the project prior to the final semester."
]

samples = [
    "The students who do not choose the original research option",
    "The students who chose to take the class",
    "All students who turned the survey in",
    "All mentors who were present on the last day of the semester",
    "The students who did not receive an A in CEEN 4020"
]

frequency = [
    "During the Fall and Spring, but no during the summer",
    "During the summer only",
    "During the spring semester only"
]

thresholds = [
    "Students score competence in all sections of rubric",
    "Students receive a pass from 4 out of 5 board members",
    "All survey items were rated at least adequate",
    "The student received high marks on the evaluation",
    "The student mastered a majority of the content"
]

assessmentVersion = Recipe(AssessmentVersion,
    report = foreign_key(report),
    slo = foreign_key(sloInReport),
    assessment = foreign_key(assessment),
    description = cycle(descriptions),
    where = cycle(wheres),
    sampleDescription = cycle(samples),
    frequency = cycle(frequency),
    threshold = cycle(thresholds)
)

