"""
File contains forms related to inputting data points
"""
from django import forms
from django_summernote.widgets import SummernoteWidget
from makeReports.models import AssessmentAggregate
from makeReports.choices import SLO_STATUS_CHOICES
from .cleaners import CleanSummer


class AddDataCollection(forms.Form):
    """
    Form to add data
    """
    dataRange = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'class':'form-control col-6'}), label="Data Collection Range")
    numberStudents = forms.IntegerField(widget= forms.NumberInput(attrs={'class':'form-control col-3'}), label="Number of Students Sampled")
    overallProficient = forms.IntegerField(widget= forms.NumberInput(attrs={'class':'form-control col-2','addon_after':'%','placeholder':'Percentage'}), label="Percentage of Students who Met/Exceeded Threshold Proficiency")

class SLOStatusForm(forms.Form):
    """
    Form to update SLO status
    """
    status = forms.ChoiceField(choices=SLO_STATUS_CHOICES, label="SLO Status: ", widget=forms.Select(attrs={'class':'form-control col-4'}))

class ResultCommunicationForm(CleanSummer,forms.Form):
    """
    Form to add how results are communicated
    """
    text = forms.CharField(
        widget=SummernoteWidget(attrs={'style':'width:750px'}), 
        label="Describe how results are communicated within the program. Address each SLO."
        )
    summer_max_length = 3000
class AssessmentAggregateForm(forms.ModelForm):
    class Meta:
        """
        Defines the model, fields, and widgets for the ModelForm superclass
        to use to build the form
        """
        model = AssessmentAggregate
        fields = ['aggregate_proficiency']
        widgets = {
            'aggregate_proficiency': forms.NumberInput(attrs={'class':'form-control col-2','addon_after':"%"})
        }
