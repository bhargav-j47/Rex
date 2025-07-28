from rest_framework import serializers
from .models import Submission


class submitSerializer(serializers.ModelSerializer):

    class Meta:
        model=Submission
        fields=["input","exp_result","language","src","timeLimit","memLimit"]
        extra_kwargs = {
                #'Setlimit': {'required': False, 'allow_blank': True},
                'timeLimit': {'required': False, 'allow_null': True},
                'memoryLimit': {'required': False, 'allow_null': True}
            }


class checkSerializer(serializers.ModelSerializer):

    class Meta:
        model=Submission
        fields="__all__"
