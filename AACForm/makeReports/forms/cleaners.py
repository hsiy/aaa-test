"""
This file contains class and method related to cleaning user input
"""
import re
import bleach
from django.core.exceptions import ValidationError

class CleanSummer():
    """
    Assumes the plugin Summernote is being used as a widget for a field called text,
    which this class then implements the cleaning method for
    """
    def clean_text(self):
        """
        Cleans the user input on the text field, and checks maximum length
        
        Returns:
            str : cleaned input
        Raises:
            ValidationError : when text is too long after being cleaned
        """
        data = self.cleaned_data['text']
        max_length = self.summer_max_length
        cleaned = cleanText(data)
        if len(cleaned)>max_length:
            raise ValidationError("This text has length "+str(len(cleaned))+", when the maximum is "+str(max_length))
        return cleaned
def cleanText(txt):
    """
    This code removes unnecessary markup - resulting from malice or Microsoft office adding thousands of lines of markup

    Args:
        txt (str): text to be cleaned
    """
    out = txt
    #sS = /(\n|\r| class=(")?Mso[a-zA-Z]+(")?)/g;
    #out = txt.replace(sS, ' ');
    out = re.sub("(\n|\r| class=\\\"*Mso[a-zA-Z]+\\\"*)"," ",txt)
    #var nL = /(\n)+/g;
    #   out = out.replace(nL, nlO);
    out = re.sub("(\n)+"," ",out) 
    return bleach.clean(
        out,
        tags= ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol','u', 'strong', 'ul','table','tr','td','tbody','p','br','hr','span','img'],
        attributes = {'*':['style'],'a': ['href', 'title'], 'abbr': ['title'], 'acronym': ['title'],'table':['class']},
        styles = ['color','text-decoration','background-color','text-align','font-weight','line-height','margin-left','margin-right','margin'],
        strip=True)

