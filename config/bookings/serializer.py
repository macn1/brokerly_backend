from rest_framework import serializers
from .models import LeadRequest

class LeadRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadRequest
        fields = "__all__"
        read_only_fields = ["request_status", "created", "user"]
