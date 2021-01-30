"""
Holds static choice tuples that should not change
"""
BLOOMS_CHOICES = (
    ('', '------'),
    ("KN","Knowledge"),
    ("CO","Comprehension"),
    ("AP", "Application"),
    ("AN", "Analysis"),
    ("SN","Synthesis"),
    ("EV", "Evaluation"))
RUBRIC_GRADES_CHOICES = (
    ("DNM","Does Not Meet/Did Not Include"),
    ("MC", "Meets with Concerns"),
    ("ME", "Meets Established"))
LEVELS = (
    ("UG", "Undergraduate"),
    ("GR", "Graduate"))
SECTIONS = (
    (1,"I. Student Learning Outcomes"),
    (2,"II. Assessment Methods"),
    (3,"III. Data Collection and Analysis"),
    (4,"IV. Decisions and Actions"))
DOMAIN_CHOICES = (
    ("E", "Examination"),
    ("P","Product"),
    ("F","Performance"))
#To prevent breaking filtering, met, partially met, not met, and unknown should maintain their positions
#However, changing the display name does not matter
SLO_STATUS_CHOICES = (
    ("Met", "Met"), 
    ("Partially Met", "Partially Met"), 
    ("Not Met", "Not Met"), 
    ("Unknown", "Unknown"))
FREQUENCY_CHOICES = (
    ("S","Once/semester"),
    ("Y","Once/year"),
    ("O","Other")    
)
#if one of these is deleted or changed, the old setting will stay in the database
#Always make sure to update todos.py and report_entry_extra_views.py
POSSIBLE_REQS = (
    ("author","Report author"),
    ("dateRange","Date range for reported data"),
    ("sloCount", "At least one SLO"),
    ("sloComm","Description of how SLOs are communicated"),
    ("assess","At least one assessment per SLO"),
    ("directAssess","At least one direct assessment per SLO"),
    ("data","Data for every measure of every SLO"),
    ("agg","Aggregate value for every measure of every SLO"),
    ("status","SLO status for every SLO"),
    ("results","Description of how results are communicated with stakeholders"),
    ("decAct","Description of decisions and actions for each SLO")
)