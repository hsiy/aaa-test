"""
Forms related to AAC grading reports
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django_summernote.widgets import SummernoteWidget
from makeReports.models import RubricItem
from makeReports.choices import RUBRIC_GRADES_CHOICES
from .cleaners import cleanText, CleanSummer


class SectionRubricForm(forms.Form):
    """
    Form to grade one section of a report based upon a rubric
    """
    def __init__(self, *args, **kwargs):
        """
        Initializes form with fields for each rubric item

        Keyword Args:
            rubricItems (QuerySet): rubric items for the section
        """
        rubricItems = kwargs.pop('rubricItems')
        super(SectionRubricForm, self).__init__(*args, **kwargs)
        for rI in rubricItems:
            self.fields['rI'+str(rI.pk)] = forms.ChoiceField(
                choices=RUBRIC_GRADES_CHOICES, 
                widget=forms.RadioSelect,
                label=mark_safe(rI.text),
                required=False
                )
            #required=False so allow partial completion of the form
        self.fields['section_comment'] = forms.CharField(
            required=False, 
            widget=SummernoteWidget(
                attrs={'style':'width:445px','summernote': {'width' : '415px'}}))
    def clean_section_comment(self):
        """
        Cleans the markup of the comment
        
        Returns:
            str : cleaned input
        Raises:
            ValidationError : when text is too long after being cleaned
        """
        data = self.cleaned_data['section_comment']
        max_length = 2000
        cleaned = cleanText(data)
        if len(cleaned)>max_length:
            raise ValidationError("This text has length "+str(len(cleaned))+", when the maximum is "+str(max_length))
        return cleaned
class RubricItemForm(forms.ModelForm):
    """
    Form to create a new rubric item
    """
    class Meta:
        """
        Defines the model type, fields, labels, and widgets for the ModelForm superclass to
        use to build the form
        """
        model = RubricItem
        fields = ['text','abbreviation','section','order','DMEtext','MEtext','EEtext']
        labels = {
            'text':'Category text',
            'abbreviation':'Abbreviation (optional)',
            'section':'Section number',
            'order':'Order position of item (lower numbers will be displayed first) (optional)',
            'DMEtext':'Did not meet expectations text',
            'MEtext':"Met expectations with concerns text",
            'EEtext':'Met expectations established text'
        }
        widgets ={
            'text': SummernoteWidget(attrs={'style':'width:750px'}),
            'DMEtext':SummernoteWidget(attrs={'style':'width:750px'}),
            'MEtext':SummernoteWidget(attrs={'style':'width:750px'}),
            'EEtext':SummernoteWidget(attrs={'style':'width:750px'})
        }
    def clean_text(self):
        """
        Cleans user input of field text
        
        Returns:
            str : cleaned input
        Raises:
            ValidationError : when text is too long after being cleaned
        """
        data = self.cleaned_data['text']
        max_length = 1000
        cleaned = cleanText(data)
        if len(cleaned)>max_length:
            raise ValidationError("This text has length "+str(len(cleaned))+", when the maximum is "+str(max_length))
        return cleaned
    def clean_DMEtext(self):
        """
        Cleans user input of field DMEtext
        
        Returns:
            str : cleaned input
        Raises:
            ValidationError : when text is too long after being cleaned
        """
        data = self.cleaned_data['DMEtext']
        max_length = 1000
        cleaned = cleanText(data)
        if len(cleaned)>max_length:
            raise ValidationError("This text has length "+str(len(cleaned))+", when the maximum is "+str(max_length))
        return cleaned
    def clean_MEtext(self):
        """
        Cleans user input of field MEtext
        
        Returns:
            str : cleaned input
        Raises:
            ValidationError : when text is too long after being cleaned
        """
        data = self.cleaned_data['MEtext']
        max_length = 1000
        cleaned = cleanText(data)
        if len(cleaned)>max_length:
            raise ValidationError("This text has length "+str(len(cleaned))+", when the maximum is "+str(max_length))
        return cleaned
    def clean_EEtext(self):
        """
        Cleans user input of field EEtext
        
        Returns:
            str : cleaned input
        Raises:
            ValidationError : when text is too long after being cleaned
        """
        data = self.cleaned_data['EEtext']
        max_length = 1000
        cleaned = cleanText(data)
        if len(cleaned)>max_length:
            raise ValidationError("This text has length "+str(len(cleaned))+", when the maximum is "+str(max_length))
        return cleaned
class DuplicateRubricForm(forms.Form):
    """
    Form to duplicate a rubric (given the rubric) and set the new name
    """
    #rubToDup = forms.ModelChoiceField(label="Rubric to duplicate",queryset=Rubric.objects,widget=forms.HiddenInput(),required=False)
    new_name = forms.CharField(max_length=1000)
class SubmitGrade(forms.Form):
    """
    Form to submit rubric
    """
    override = forms.BooleanField(widget=forms.CheckboxInput(), required=False,label="Submit without reviewing all rubric items")
    def __init__(self, *args, **kwargs):
        """
        Initializes form and sets valid on the instance

        Keyword Args:
            valid (bool) : the grading is complete
        """
        self.valid = kwargs.pop('valid')
        super(SubmitGrade, self).__init__(*args, **kwargs)
        if self.valid:
            self.fields['override'].widget = forms.HiddenInput()
    def clean(self):
        """
        Cleans form and raises validation error if not valid

        Raises:
            ValidationError : the grading is not complete
        """
        super().clean()
        if not (self.valid or self.cleaned_data['override']):
            raise forms.ValidationError("Not all rubric items have been graded.")
class OverallCommentForm(CleanSummer,forms.Form):
    """
    Form for the overall comment
    """
    text = forms.CharField(widget=SummernoteWidget(attrs={'style':'width:445px','summernote': {'width' : '415px'}}),label="",max_length=2000)
    summer_max_length = 2000