"""
This file contains recipes to create AAC admin models

Attributes:
    college (Recipe): recipe to create :class:`~makeReports.models.aac_models.College` model
    department (Recipe): recipe to create :class:`~makeReports.models.aac_models.Department` model
    degreeProgram (Recipe): recipe to create :class:`~makeReports.models.aac_models.DegreeProgram` model
    announcement (Recipe): recipe to create :class:`~makeReports.models.aac_models.Announcement` model
"""
from itertools import cycle
from model_bakery.recipe import Recipe, foreign_key
from makeReports.models.aac_models import Announcement, College, Department, DegreeProgram


college_names = ["College of Information Science and Technology","College of Arts and Sciences","College of Business", "College of Engineering","College of Education","College of Health and Kineseology"]
department_names = ["English","Mathematics","Computer Science","Computer Engineering","Business Administration","History","Secondary Education","Elementary Education","Biology","Physical Education"]

dp_names = ["English","Electrical Engineering","Mathematics","Statistics","Computer Science","IT Innovations","Civil Engineering","Secondary Education","Business",'Biology',"Ancient History","Black Studies","Physics"]

startingYear = [2015,2016,2017,2018,2019,2020,2021,2022,2035,2037]
cyclelength = [0,1,2,3,4,5,6,7,8,10]

announcements = ['All reports must be completed by the end of this week.',"The system will be down for maitenance starting next week. Please plan accordingly.","Our newest committee member is Sandra Lee. Please make sure to welcome her and ask any questions if needed via email.","Reports will be assigned next week."]

college = Recipe(College,
    name = cycle(college_names)
)
department =  Recipe(Department,
    name = cycle(department_names),
    college = foreign_key(college)
)
degreeProgram = Recipe(DegreeProgram,
    name = cycle(dp_names),
    department = foreign_key(department),
    startingYear = cycle(startingYear),
    cycle = cycle(cyclelength)
)
announcement = Recipe(Announcement,
    text = cycle(announcements)
)