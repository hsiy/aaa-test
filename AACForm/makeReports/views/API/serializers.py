"""
This file contains the JSON APIs used
"""
from rest_framework import serializers
from makeReports.models import (
    Assessment,
    DegreeProgram, 
    Department, 
    Graph,
    SLO, 
    SLOInReport
)

class DeptSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes departments to JSON with the primary key and name
    """
    class Meta:
        """
        Defines the model type and fields for the superclass
        to use to build the serializer.
        """
        model = Department
        fields = ['pk','name']
class ProgSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes degree programs to JSON with the primary key, name, and level
    """
    class Meta:
        """
        Defines the model type and fields for the superclass
        to use to build the serializer
        """
        model = DegreeProgram
        fields = ['pk', 'name', 'level']
class SLOserializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes SLOs to JSON with the primary key and name
    """
    class Meta:
        """
        Defines the model type and fields for the superclass
        to use to build the serializer
        """
        model = SLOInReport
        fields = ['pk', 'goalText']
class SLOParentSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes :class:`~makeReports.models.slo_models.SLO` into just its primary key
    """
    class Meta:
        """
        Defines the model type and fields for the superclass
        to use to build the serializer
        """
        model = SLO
        fields = ['pk']
class SLOSerializerWithParent(serializers.HyperlinkedModelSerializer):
    """
    Serializes SLOs (:class:`~makeReports.models.slo_models.SLOInReport`) to JSON with the primary key and name and primary key of SLO
    """
    slo = SLOParentSerializer()
    class Meta:
        """
        Defines the model type and fields for the superclass
        to use to build the serializer
        """
        model = SLOInReport
        fields = ['pk', 'goalText','slo']
class AssessmentParentSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes parent assessments (:class:`~makeReports.models.assessment_models.Assessment`) into its primary key and title
    """
    class Meta:
        """
        Defines the model type and fields for the superclass
        to use to build the serializer
        """
        model = Assessment
        fields = ['pk','title']
class AssessmentSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes assessments (:class:`~makeReports.models.assessment_models.AssessmentVersion`) to JSON with the primary key and and title
    """
    assessment = AssessmentParentSerializer()
    class Meta:
        """
        Defines the model type and fields for the superclass
        to use to build the serializer
        """
        model = SLOInReport
        fields = ['pk', 'assessment']
class FileSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes graphs to JSON with all fields 
    """
    class Meta:
        """
        Defines the model type and fields for the superclass
        to use to build the serializer
        """
        model = Graph
        fields = "__all__"
