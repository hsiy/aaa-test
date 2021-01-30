"""
File with forms that do not fit elsewhere
"""
from django import forms

class SubmitReportForm(forms.Form):
    """
    Dummy form to submit report
    """
    hidden = forms.CharField(max_length=5,widget=forms.HiddenInput(), required=False)
    def __init__(self, *args, **kwargs):
        """
        Initializes form and sets the valid and error message on the instance

        Keyword Args:
            valid (bool) : if report is valid to be submitted
            eMsg (str): error message
        """
        self.valid = kwargs.pop('valid')
        self.error = kwargs.pop('eMsg')
        super(SubmitReportForm, self).__init__(*args, **kwargs)
    def clean(self):
        """
        Cleans form and checks if valid

        Raises:
            ValidationError : Report is not complete
        """
        super().clean()
        if not self.valid:
            raise forms.ValidationError(self.error)