from rest_framework import serializers
from .models import LeadRequest, LeadVisit
from apartments.models import Apartments
from authentication.models import User

# Mapping from LeadVisit status → Apartment availability
LEAD_TO_APARTMENT_STATUS = {
    "Interested": "Pending",
    "Holding": "Pending",
    "Rejected": "Pending",
    "Booked": "Confirmed",
    "Paid": "Confirmed",
}


class LeadVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadVisit
        fields = [
            "id",
            "lead",
            "visit_date",
            "status",
            "amount_paid",
            "pending_amount",
            "remarks",
        ]
        read_only_fields = ["id", "visit_date"]

    def update(self, instance, validated_data):
        new_status = validated_data.get("status", instance.status)
        instance = super().update(instance, validated_data)

        # Sync apartment availability when visit status changes
        apartment_status = LEAD_TO_APARTMENT_STATUS.get(new_status)
        if apartment_status:
            apartment = instance.lead.apartment
            apartment.availability = apartment_status
            apartment.save(update_fields=["availability"])

        return instance


class LeadRequestSerializer(serializers.ModelSerializer):
    visits = LeadVisitSerializer(many=True, read_only=True)

    apartment_id = serializers.IntegerField(source="apartment.id", read_only=True)
    apartment_name = serializers.CharField(source="apartment.name", read_only=True)
    apartment_price = serializers.CharField(source="apartment.price", read_only=True)

    vendor_username = serializers.CharField(source="vendor_name.name", read_only=True)

    class Meta:
        model = LeadRequest
        fields = [
            "id",
            "vendor_name",  # FK ID (writable)
            "vendor_username",  # resolved name (read-only)
            "name",
            "email",
            "mobile",
            "apartment",  # FK ID (writable, for POST)
            "apartment_id",  # same ID but explicit (read-only)
            "apartment_name",  # read-only
            "apartment_price",  # read-only
            "message",
            "request_status",
            "request_mode",
            "created",
            "visits",
        ]
        read_only_fields = [
            "id",
            "created",
            "apartment_id",
            "apartment_name",
            "apartment_price",
            "vendor_username",
        ]

    def update(self, instance, validated_data):
        new_status = validated_data.get("request_status", instance.request_status)
        instance = super().update(instance, validated_data)

        # Sync apartment availability when lead request_status changes
        REQUEST_TO_APARTMENT_STATUS = {
            "Requested": "Pending",
            "Approved": "Confirmed",
            "Holding": "Pending",
            "Rejected": "Pending",
        }
        apartment_status = REQUEST_TO_APARTMENT_STATUS.get(new_status)
        if apartment_status:
            instance.apartment.availability = apartment_status
            instance.apartment.save(update_fields=["availability"])

        return instance


class LeadBookingListSerializer(serializers.ModelSerializer):
    apartment_name = serializers.CharField(source="apartment.name", read_only=True)
    customer_name = serializers.CharField(source="name", read_only=True)
    
    amount_paid = serializers.SerializerMethodField()
    pending_amount = serializers.SerializerMethodField()
    visit_status = serializers.SerializerMethodField()  # ✅ latest visit status

    def get_latest_visit(self, obj):
        return obj.visits.order_by('-visit_date').first()

    def get_visit_status(self, obj):
        visit = self.get_latest_visit(obj)
        return visit.status if visit else "No Visit Yet"

    def get_amount_paid(self, obj):
        visit = self.get_latest_visit(obj)
        return str(visit.amount_paid) if visit else "0.00"

    def get_pending_amount(self, obj):
        visit = self.get_latest_visit(obj)
        return str(visit.pending_amount) if visit else "0.00"

    class Meta:
        model = LeadRequest
        fields = [
            'id',
            'apartment_name',
            'customer_name',
            'mobile',
            'email',
            'request_status',   # lead level status (Requested/Approved etc)
            'visit_status',     # ✅ latest visit status (Interested/Booked/Paid etc)
            'request_mode',
            'amount_paid',
            'pending_amount',
            'created',
        ]

class ApartmentTransactionSerializer(serializers.Serializer):
    id           = serializers.IntegerField()
    name         = serializers.CharField()
    availability = serializers.CharField()
    paid         = serializers.DecimalField(max_digits=10, decimal_places=2)
    pending      = serializers.DecimalField(max_digits=10, decimal_places=2)


class VendorTransactionSerializer(serializers.Serializer):
    id               = serializers.IntegerField()
    name             = serializers.CharField()
    email            = serializers.EmailField()
    total_apartments = serializers.IntegerField()
    total_paid       = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_pending    = serializers.DecimalField(max_digits=12, decimal_places=2)
    apartments       = ApartmentTransactionSerializer(many=True)