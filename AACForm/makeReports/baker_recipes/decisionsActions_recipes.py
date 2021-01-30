"""
This file contains recipes to create decisions and actions models

Attributes:
    decisionsActions (Recipe): recipe for creating :class:`~makeReports.models.decisionsActions_models.DecisionsActions` model
"""
from itertools import cycle
from model_bakery.recipe import Recipe, foreign_key
from makeReports.models.decisionsActions_models import DecisionsActions
from .slo_recipes import sloInReport


dAs = [
    "We decided to update our program to include for review sessions for the exam. Student will be required to attend at least three and encouraged to attend them all. We hope this better improves SLO 4.",
    "SLO 1	Decision making process: Based on our data reported, we achieved our proficiency target for this SLO. The project evaluation \
         for the final paper, and the evaluation portion of the progress reports will be examined closely as we collect more data to ensure that our students are able to\
              adequately evaluate their activities and performance in regard to disciplinary knowledge. It is important to us to ensure that students are able to integrate their knowledge,\
                   understanding and skills to analyze the information in a real world setting.  In regards to the comprehensive exam, we may choose to examine each question in regards to whether it focuses on this \
                       specific SLO and record whether a revision is needed for each individual question. We are cautious when making any decisions because our sample size is small for some of our indicators. \
        Decision maker(s): Primarily the assessment and practicum coordinator, along with the graduate program chair; however, the entire faculty will be involved in this discussion and final decision at our next faculty meeting in February, 2018.\
        Decision timeline:  Preliminary decisions were made when preparing this report in January 2018; however, as indicated above, no final decisions will be made until our February 2018 faculty meeting. \
        Data used for decision: Data reported in the above table from Spring, Summer and Fall 2017.\
        Action Timeline: Based on our February 2018 faculty meeting (and feedback from our EAB meeting in January), we will begin to make\
            necessary changes immediately, in spring 2018. Further, we will continue to assess each semester to increase our sample size for analysis.",
    "SLO 2	Decision making process: We also achieved proficiency for SLO 2; however, some of our data sources were too small to appropriately assess. Thus, as with SLO 1, we will be mindful of our students’ progress on the project evaluation for the final paper, \
        and the evaluation portion of the progress reports to ensure that our students are satisfactorily engaging in critical thinking when moving to the practicum experience, and writing their comprehensive exam responses. If there is reason for concern, we will aim to engage in more opportunities\
             for discussion of concepts, theories and knowledge in class or on discussion boards, and also through writing assignments. We are cautious when making any decisions because our sample size is small for some of our indicators. \
        Decision maker(s): Primarily the assessment and practicum coordinator, along with the graduate program chair; however, the entire faculty will be involved in this discussion and final decision at our next faculty meeting in February, 2018.\
        Decision timeline:  Preliminary decisions were made when preparing this report in January 2018; however, as indicated above, no final decisions will be made until our February 2018 faculty meeting. \
        Data used for decision: Data reported in the above table from Spring, Summer and Fall 2017.\
        Action Timeline: Based on our February 2018 faculty meeting (and feedback from our EAB meeting in January), we will begin to make necessary changes immediately, in spring 2018. Further, we will continue to assess each semester to increase our sample size for analysis."
]
decisionsActions = Recipe(DecisionsActions,
    sloIR = foreign_key(sloInReport),
    text = cycle(dAs)
)

