"""
This tests the grading forms work as expected
"""
from django.test import TestCase
from makeReports.models import RubricItem
from model_bakery import baker
from makeReports.forms import (
    DuplicateRubricForm, 
    OverallCommentForm, 
    RubricItemForm, 
    SectionRubricForm, 
    SubmitGrade
)
from makeReports.choices import RUBRIC_GRADES_CHOICES

class RubricFormsTests(TestCase):
    """
    Tests forms related to the rubric forms
    """
    def test_section_rubric_valid(self):
        """
        Tests that SectionRubricForm accepts valid data
        """
        rI = baker.make("RubricItem")
        rI2 = baker.make("RubricItem")
        f = SectionRubricForm({
            'rI'+str(rI.pk): RUBRIC_GRADES_CHOICES[0][0],
            'rI'+str(rI2.pk): RUBRIC_GRADES_CHOICES[1][0],
            'section_comment':"You did a good job examining ways to improve."
        },rubricItems= RubricItem.objects.all())
        self.assertTrue(f.is_valid())
    def test_section_rubric_choice_failed(self):
        """
        Tests that SectionRubricForm fails when the rubric item is not one of the choices
        """
        rI = baker.make("RubricItem")
        rI2 = baker.make("RubricItem")
        f = SectionRubricForm( {
            'rI'+str(rI.pk): RUBRIC_GRADES_CHOICES[0][0],
            'rI'+str(rI2.pk): "not a valid choice",
            'section_comment':"You need to work more on your data collection."
        },rubricItems= RubricItem.objects.all())
        self.assertFalse(f.is_valid())
    def test_section_rubric_toolong(self):
        """
        Tests the form is invalid when the section comment is too long
        """
        rI = baker.make("RubricItem")
        f = SectionRubricForm({
            'rI'+str(rI.pk): RUBRIC_GRADES_CHOICES[0][0],
            'section_comment':"This simply will not do."*200
        },rubricItems= RubricItem.objects.all())
        self.assertFalse(f.is_valid())      
    def test_item_form_valid(self):
        """
        Tests that RubricItemForm accepts valid data
        """
        f = RubricItemForm({
            'text':'The report uses assessments highly aligned with the SLOs.',
            'abbreviation':'JK',
            'section':3,
            'order':5,
            'DMEtext':'There are no assessments.',
            'MEtext':'There are mostly assessments for every SLO.',
            'EEtext':'There are more than one assessment for every SLO.'
        })
        self.assertTrue(f.is_valid())
    def test_item_form_nonint(self):
        """
        Tests that the RubricItemForm rejects form with non-integer section
        """
        f = RubricItemForm({
            'text':'The report uses SLOs that demand high expectations.',
            'abbreviation':'JK',
            'section':3.3,
            'order':5,
            'DMEtext':'There are no SLOs.',
            'MEtext':'Only one SLO represents higher thinking.',
            'EEtext':'All SLOs demand higher thinking.'
        })
        self.assertFalse(f.is_valid())
    def test_dup_rub(self):
        """
        Tests that the duplicate rubric form accepts valid data
        """
        f = DuplicateRubricForm({
            'new_name': "Rubric for the 2019-2020 school year"
        })
        self.assertTrue(f.is_valid())
    def test_dup_rub_toolong(self):
        """
        Tests the form rejects when the new name is too long
        """
        f = DuplicateRubricForm({
            'new_name': "Rubric for the 2019-2020 school year"*300
        })
        self.assertFalse(f.is_valid())
    def test_submitGrade(self):
        """
        Tests the SubmitGrade form properly takes true argument
        """
        f = SubmitGrade({
            'hidden':'a'
        },valid=True)
        self.assertTrue(f.is_valid())
    def test_submitGradeFalse(self):
        """
        Tests the SubmitGrade form properly fails when given a false argument
        """
        f = SubmitGrade({
            'hidden':''
        },valid=False)
        self.assertFalse(f.is_valid())
    def test_overallcomment(self):
        """
        Test the OverallCommentForm properly allows valid text
        """
        f = OverallCommentForm({
            'text':'The report did a <b>great</b> job looking on how to make the program better.'
        })
        self.assertTrue(f.is_valid())
    