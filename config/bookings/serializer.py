from rest_framework import serializers
from .models import LeadRequest,LeadVisit



class LeadVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadVisit
        fields = [
            'id',
            'lead',
            'visit_date',
            'status',
            'amount_paid',
            'pending_amount',
            'remarks'
        ]
        read_only_fields = ['id', 'visit_date']
class LeadRequestSerializer(serializers.ModelSerializer):
    visits = LeadVisitSerializer(many=True, read_only=True)
    apartment_name = serializers.CharField(source="apartment.name", read_only=True)
    vendor_name = serializers.CharField(source="vendor_name.name", read_only=True)

    apartment_price = serializers.CharField(source='apartment.price',read_only=True)
    class Meta:
        model = LeadRequest
        fields = [
            'id',
            'vendor_name',
            'name',
            'email',
            'mobile',
            'apartment',
            'message',
            'request_status',
            'request_mode',
            'created',
            'visits',
            'apartment_name',
            'apartment_price'
        ]
        read_only_fields = ['id', 'created','apartment_name','apartment_price']



