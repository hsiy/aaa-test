"""
This tests the data collection related forms work as expected
"""
from django.test import TestCase
from makeReports.forms import AddDataCollection, AssessmentAggregateForm, ResultCommunicationForm, SLOStatusForm
from makeReports.choices import SLO_STATUS_CHOICES

class DataCollectionFormTests(TestCase):
    """
    Tests forms related to data collection work as expected
    """
    def test_add_valid(self):
        """
        Tests AddDataCollection accepts valid data
        """
        f = AddDataCollection({
            'dataRange':"Spring 2019",
            'numberStudents':993,
            'overallProficient':93
        })
        self.assertTrue(f.is_valid())
    def test_add_notint(self):
        """
        Tests AddDataCollection rejects non-integer number of students
        """
        f = AddDataCollection({
            'dataRange':'Fall 2019 - Spring 202',
            'numberStudents': 93.2,
            'overallProficient':83
        })
        self.assertFalse(f.is_valid())
    def test_status_valid(self):
        """
        Tests that SLOStatusForm accepts valid form
        """
        f = SLOStatusForm({
            'status': SLO_STATUS_CHOICES[0][0]
        })
        self.assertTrue(f.is_valid())
    def test_status_notchoice(self):
        """
        Tests that SLOStatusForm reject not choices
        """
        f = SLOStatusForm({
            'status':3
        })
        self.assertFalse(f.is_valid())
    def test_result_comm_valid(self):
        """
        Test ResultCommunicationForm accepts valid data
        """
        f = ResultCommunicationForm({
            'text':'xys'*399
        })
        self.assertTrue(f.is_valid())
    def test_result_comm_toolong(self):
        """
        Test ResultCommunicationForm rejects invalid data when text is too long
        """
        f = ResultCommunicationForm({
            'text':'x'*4000
        })
        self.assertFalse(f.is_valid())
    def test_agg_valid(self):
        """
        Test that AssessmentAggregateForm accepts valid data
        """
        f = AssessmentAggregateForm({
            'aggregate_proficiency':33
        })
        self.assertTrue(f.is_valid())
    def test_agg_notNumber(self):
        """
        Test that AssessmentAggregateForm rejects non-numbers
        """
        f = AssessmentAggregateForm({
            'aggregate_proficiency':"at least 80"
        })
        self.assertFalse(f.is_valid())