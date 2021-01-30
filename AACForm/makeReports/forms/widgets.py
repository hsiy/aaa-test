"""
Includes custom widgets, which change how forms are displayed
"""
import os
from django import forms
from django.conf import settings

class SLOChoicesJSWidget(forms.widgets.Select):
    """
    Widget that uses the Choices Javascript plugin for a drop-down
    """
    template_name = 'widgets/select.html'
    option_template_name = 'widgets/option.html'
    class Media:
        css = {'all': (
            "https://cdn.jsdelivr.net/npm/choices.js/public/assets/styles/choices.min.css",
            os.path.join(settings.STATIC_URL,'css/slo_choices.css')
             )}
        js = (
            "https://cdn.jsdelivr.net/npm/choices.js/public/assets/scripts/choices.min.js",
            os.path.join(settings.STATIC_URL,'extPlugin/choices-widget.js'))
class SLOMultipleChoicesJSWidget(forms.widgets.SelectMultiple):
    """
    Widget that uses the Choices Javascript plugin for a drop-down and allows for mutliple choices
    """
    template_name = 'widgets/selectMultiple.html'
    option_template_name = 'widgets/option.html'
    class Media:
        css = {'all': (
            "https://cdn.jsdelivr.net/npm/choices.js/public/assets/styles/choices.min.css",
            os.path.join(settings.STATIC_URL,'css/slo_choices.css')
             )}
        js = (
            "https://cdn.jsdelivr.net/npm/choices.js/public/assets/scripts/choices.min.js",
            os.path.join(settings.STATIC_URL,'extPlugin/choices-widget.js'))
class StkChoicesJSWidget(forms.widgets.Select):
    """
    Widget that uses the Choices Javascript plugin for a drop-down for stakeholder
    """
    template_name = 'widgets/select.html'
    option_template_name = 'widgets/option.html'
    class Media:
        css = {'all': (
            "https://cdn.jsdelivr.net/npm/choices.js/public/assets/styles/choices.min.css",
            os.path.join(settings.STATIC_URL,'css/slo_choices.css')
             )}
        js = (
            "https://cdn.jsdelivr.net/npm/choices.js/public/assets/scripts/choices.min.js",
            os.path.join(settings.STATIC_URL,'extPlugin/choice-widget-stk.js'))
