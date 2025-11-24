from rest_framework import serializers
from .models import LeadRequest

class LeadRequestSerializer(serializers.ModelSerializer):
    apartment_name = serializers.CharField(source='apartment.name', read_only=True)

    class Meta:
        model = LeadRequest
        fields = "__all__"


