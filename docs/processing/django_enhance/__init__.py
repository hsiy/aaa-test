"""
Sphinx extension to better format and document Django objects

Lightly modified from: https://github.com/edoburu/sphinxcontrib-django
Modifications:
    Meta classes are still included in the documentation
    The extra form processing is also applied to subclasses of ModelForm and not just subclasses of Form
"""
import sys

import django

__version__ = "0.5"


def setup(app):
    """Allow this module to be used as sphinx extension.
    This attaches the Sphinx hooks.
    :type app: sphinx.application.Sphinx
    """
    from . import docstrings
    from . import roles

    # Setup both modules at once. They can also be separately imported to
    # use only fragments of this package.
    docstrings.setup(app)
    roles.setup(app)


#: Example Intersphinx mapping, linking to project versions
python_version = ".".join(map(str, sys.version_info[0:2]))
django_version = ".".join(map(str, django.VERSION[0:2]))
intersphinx_mapping = {
    "python": ("https://docs.python.org/" + python_version, None),
    "django": (
        "https://docs.djangoproject.com/en/{}/".format(django_version),
        "https://docs.djangoproject.com/en/{}/_objects/".format(django_version),
    ),
    "braces": ("https://django-braces.readthedocs.org/en/latest/", None),
    "select2": ("https://django-select2.readthedocs.org/en/latest/", None),
    "celery": ("https://celery.readthedocs.org/en/latest/", None),
}