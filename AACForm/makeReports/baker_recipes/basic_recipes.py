"""
This file contains recipes to create basic models

Attributes:
    report (Recipe): recipe to create :class:`~makeReports.models.basic_models.Report` model
    profile (Recipe): recipe to create :class:`~makeReports.models.basic_models.Profile` model

"""
from itertools import cycle
from model_bakery.recipe import Recipe, foreign_key
from makeReports.models.basic_models import Profile, Report
from .aac_recipes import degreeProgram, department

first_names = ['Ada',"Ida","Grant","Shannon","Steve","Loki","Matthew","Allison","Mary-Rose","Jonathan"]
last_names = ["McCarty","Dargy","Jacobson","Williams-Jones","Laverne","Tikisip","Rogers","Stark","Adams","Ali"]
full_names = ['Ada McCarty',"Ida Dargy","Ida McCarty","Grant Jacobson","Shannon Jacobson","Loki Williams-Jones","Matthew Laverne","Ada Laverne","Allion Tikisip","Mary-Rose Tikisip","Jonathan Rogers","Johnathan Stark","Amy Adams","Heather Ali","Lucas Ali","John-Jay La'tifa"]
emails = ["jsdoe@unomaha.edu","alexbatter@unomaha.edu", "awatts2@unomaha.edu","bNickers@nebraska.edu","alexJames5@gmail.com","zanderJonesUNL@gmail.com"]


startingYear = [2015,2016,2017,2018,2019,2020,2021,2022,2035,2037]
semesterDates = ['Fall 2015-Spring 2020', "Fall 2019", "Summer 2018", "Spring 2017-Fall 2018", "Spring 2018, Fall 2019, Spring 2020","Summer 2017 to Spring 2018", "Summer 2021 to Fall 2022","Fall and Spring 2017"]

comments = ["We did collect more data, however, since we changed our measures we do not have very much to report. We plan on having more data in 2019.","The students did very well on the exam, but did not do as well on the paper. We suspect this is due to grading differences.","Our degree program is new this year. We have not yet collected any data, and since the program is small, it would be hard to extrapolate.","We were very excited to add the new SLO. We managed to collect data in the past semester."]


report = Recipe(Report,
    year = cycle(startingYear),
    author = cycle(full_names),
    degreeProgram = foreign_key(degreeProgram),
    date_range_of_reported_data = cycle(semesterDates),
    section1Comment = cycle(comments),
    section2Comment = cycle(comments),
    section3Comment = cycle(comments),
    section4Comment = cycle(comments),
)

profile = Recipe(Profile,
    department = foreign_key(department),
    user__first_name = cycle(first_names),
    user__last_name = cycle(last_names),
    user__email = cycle(emails)
)

