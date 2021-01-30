"""
This file contains recipes to create data models

Attributes:
    assessmentData (Recipe): recipe to create :class:`~makeReports.models.data_models.AssessmentData` model
    assessmentAggregate (Recipe): recipe to create :class:`~makeReports.models.data_models.AssessmentAggregate` model
    resultCommunicate (Recipe): recipe to create :class:`~makeReports.models.data_models.ResultCommunicate` model
"""
from itertools import cycle
from model_bakery.recipe import Recipe, foreign_key
from makeReports.models.data_models import AssessmentAggregate, AssessmentData, ResultCommunicate
from .basic_recipes import report
from .assessment_recipes import assessmentVersion


semesterDates = ['Fall 2015-Spring 2020', "Fall 2019", "Summer 2018", "Spring 2017-Fall 2018", "Spring 2018, Fall 2019, Spring 2020","Summer 2017 to Spring 2018", "Summer 2021 to Fall 2022","Fall and Spring 2017"]
percentages = [20,17,95,87,92,84,78,91]
students = [2,20,542,212,123,75,31,10,12,44]


assessmentData = Recipe(AssessmentData,
    assessmentVersion = foreign_key(assessmentVersion),
    dataRange = cycle(semesterDates),
    overallProficient = cycle(percentages),
    numberStudents = cycle(students)
)

assessmentAggregate = Recipe(AssessmentAggregate,
    assessmentVersion = foreign_key(assessmentVersion),
    aggregate_proficiency = cycle(percentages)
)

rCs = ["We publish all data on the website. We send out emails to inform the department when new results are posted.","A weekly meeting is held. When appropriate, new results are shared during this meeting by the assessment head. Later, they are sent via email.","As a new department, practices are still being put into place. Usually the head of the department sends updated Excel reports to faculty.","The information is listed on paper available in the office."]

resultCommunicate = Recipe(ResultCommunicate,
    text = cycle(rCs),
    report = foreign_key(report)
)
