# Django modules
from django.serializers import ModelSerializer
from .models import MCPRequestLog
# Project modules

class MCPSerializer(ModelSerializer):
    class Meta:
        model = MCPRequestLog
        fields = '__all__'
