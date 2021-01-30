"""
This file contains forms to administer the website
"""
from django import forms
from makeReports.models import (
    Announcement,
    College,
    DegreeProgram,
    Department,
    GradGoal,
    Report,
    Rubric
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django_summernote.widgets import SummernoteWidget
from makeReports.choices import POSSIBLE_REQS
from .cleaners import CleanSummer

class UpdateUserForm(forms.Form):
    """
    Form to update a pre-existing user by the AAC
    """
    aac = forms.BooleanField(label="AAC member",required=False)
    department = forms.ModelChoiceField(queryset=Department.active_objects.all().order_by("name"), label="Department", required=False,widget=forms.Select(attrs={'class':'form-control col-6'}))
    first_name = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'class':'form-control col-6'}))
    last_name = forms.CharField(max_length=150,widget=forms.TextInput(attrs={'class':'form-control col-6'}))
    email = forms.CharField(max_length=30,widget=forms.EmailInput(attrs={'class':'form-control col-6'}))
class UserUpdateUserForm(forms.Form):
    """
    Form to update a user by the user themselves (fewer permissions)
    """
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class':'form-control col-6'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class':'form-control col-6'}))
    email = forms.CharField(max_length=30, widget=forms.EmailInput(attrs={'class':'form-control col-6'}))
class CreateDepartmentForm(forms.ModelForm):
    """
    Form to create new department
    """
    class Meta:
        """
        Defines the model type, fields, and widgets for use by the ModelForm superclass
        """
        model = Department
        fields = ['name', 'college']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control col-6'}),
            'college': forms.Select(attrs={'class':'form-control col-6'})
        }
    def __init__(self,*args,**kwargs):
        """
        Initializes the form and sets possible colleges to only those which are active
        """
        super(CreateDepartmentForm,self).__init__(*args,**kwargs)
        self.fields['college'].queryset=College.active_objects.all().order_by("name")
class GenerateReports(forms.Form):
    """
    Form to generate reports
    """
    year = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control col-6'}))
    rubric = forms.ModelChoiceField(queryset=Rubric.objects.order_by('-date'), widget=forms.Select(attrs={'class':'form-control col-6'}))
class MakeNewAccount(UserCreationForm):
    """
    Form for the AAC to make a new account
    """
    isaac = forms.BooleanField(required=False, label="Account for AAC member?")
    department = forms.ModelChoiceField(queryset=Department.active_objects, label="Department", required=False,widget=forms.Select(attrs={'class':'form-control col-6'}))
    college = forms.ModelChoiceField(queryset=College.active_objects.all().order_by("name"), label="College",required=False,widget=forms.Select(attrs={'class':'form-control col-6'}))
    class Meta:
        """
        Defines the model type, fields, and widgets for use by the superclass ModelForm when
        creating the form
        """
        model = User
        fields = ['email','username','password1','password2','isaac','first_name','last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'class':'form-control col-6'}),
            'username': forms.TextInput(attrs={'class':'form-control col-6'}),
            'password1': forms.PasswordInput(attrs={'class':'form-control col-6'}),
            'password2': forms.PasswordInput(attrs={'class':'form-control col-6'}),
            'first_name': forms.TextInput(attrs={'class':'form-control col-6'}),
            'last_name': forms.TextInput(attrs={'class':'form-control col-6'})
        }
    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            return valid
        if (
            self.cleaned_data["college"] and self.cleaned_data["college"]!=""
            ) and (
                not self.cleaned_data["department"] or self.cleaned_data["department"]==""
                ):
            self._errors["department"]="If a college is specified, a department must also be specified."
            return False
        return True
    def save(self, commit=True):
        """
        Upon creating a new user, both the Django User type and custom profile type must be created

        Keyword Args:
            commit (bool) : whether to actually save user to database

        Returns:
            user, profile : user and profile created
        """
        user = super(MakeNewAccount, self).save(commit=True)
        profile = user.profile
        profile.aac = self.cleaned_data['isaac']
        profile.department=self.cleaned_data['department']
        user.save()
        profile.save()
        return user, profile
class AnnouncementForm(CleanSummer,forms.ModelForm):
    """
    Form to create announcement by AAC
    """
    text = forms.CharField(widget=SummernoteWidget(attrs={'style':'width:750px'}),label="Announcement")
    summer_max_length = 2000
    class Meta:
        """
        Defines the model type, widgets, and fields for use by the ModelForm superclass to build the form
        """
        model = Announcement
        widgets = {
            'expiration': forms.SelectDateWidget(),
        }
        fields = ['text','expiration']
class GradGoalForm(CleanSummer,forms.ModelForm):
    """
    Form to create new graduate goal
    """
    text = forms.CharField(widget=SummernoteWidget(attrs={'style':'width:750px'}),label="Goal text: ")
    summer_max_length = 600
    class Meta:
        """
        Defines the model type and fields for the ModelForm superclass to use to build the form
        """
        model = GradGoal
        fields = ['text']
class GradGoalEditForm(CleanSummer,forms.ModelForm):
    """
    Form to create edit graduate goal, including possibly archiving it
    """
    text = forms.CharField(widget=SummernoteWidget(attrs={'style':'width:750px'}),label="Goal text: ")
    summer_max_length = 600
    class Meta:
        """
        Defines the model type and fields for the ModelForm superclass to use to build the form
        """
        model = GradGoal
        fields = ['active','text']

class CreateReportByDept(forms.ModelForm):
    """
    Form to create new report via a link that already gives department (but not degree program)
    """
    class Meta:
        """
        Defines the model type, fields, labels, and widgets for the superclass ModelForm
        to use to build the form.
        """
        model = Report
        fields = ['year', 'degreeProgram'] 
        labels = {
            'degreeProgram': "Degree Program"
        }
        widgets = {
            'year': forms.NumberInput(attrs={'class':'form-control col-6'}),
            'degreeProgram': forms.Select(attrs={'class':'form-control col-6'})
        }
    def __init__(self,*args,**kwargs):
        """
        Initializes form, sets the degree program options by the keyword argument and sets rubric options

        Keyword Args:
            dept (Department): department object to pick degree programs from
        """
        dept = Department.objects.get(pk=kwargs.pop('dept'))
        super(CreateReportByDept, self).__init__(*args, **kwargs)
        self.fields['degreeProgram'].queryset = DegreeProgram.objects.filter(department=dept)
        self.fields['rubric'] = forms.ModelChoiceField(queryset=Rubric.objects.all().order_by("-date"))
class CreateReportByDPForm(forms.ModelForm):
    """
    Form to create report where degree program is already picked
    """
    class Meta:
        """
        Defines the model type, fields and widgets for the ModelForm superclass to
        use to build the form
        """
        model = Report
        fields = ['year']
        widgets = {
            'year': forms.NumberInput(attrs={'class':'form-control col-6'})
        }
    def __init__(self,*args,**kwargs):
        """
        Initializes form and sets rubric options
        """
        super(CreateReportByDPForm,self).__init__(*args,**kwargs)
        self.fields['rubric'] = forms.ModelChoiceField(queryset=Rubric.objects.all().order_by("-date"))
class CreateDPByDept(forms.ModelForm):
    """
    Form to create degree program where department is given
    """ 
    accredited = forms.BooleanField(required=False, label="Externally Accredited?")
    class Meta:
        """
        Defines the model, fields, labels, and widgets for the ModelForm superclass
        to use to make a form
        """
        model = DegreeProgram
        fields = ['name','level','cycle','startingYear','accredited']
        labels = {
            'name': "Name",
            'level': "Level",
            'cycle': "Number of years between automatically assigned reports (put 0 or leave blank if there is no regular cycle)",
            'startingYear': "The first year report is assigned for cycle (leave blank if no cycle)"
        }

        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control col-6'}),
            'level': forms.Select(attrs={'class':'form-control col-4'}),
            'cycle': forms.NumberInput(attrs={'class':'form-control col-3','placeholder':'Cycle length'}),
            'startingYear': forms.NumberInput(attrs={'class':'form-control col-3', 'placeholder':'Starting year'})
        }
class RequiredReportFieldsForm(forms.Form):
    """
    Form to change which fields are required to submit a report
    """
    def __init__(self, *args, **kwargs):
        """
        Creates the form fields from the list in POSSIBLE_REQS (from choices)
        """
        super().__init__(*args,**kwargs)
        for req in POSSIBLE_REQS:
            self.fields[req[0]] = forms.BooleanField(required=False, label=req[1])
