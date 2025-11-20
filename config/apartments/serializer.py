from rest_framework import serializers
from .models import Amenity, FacilityService, Address, ApartmentImages, Apartments


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = "__all__"
        read_only_fields = ["owner"] 

class FacilityServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityService
        fields = "__all__"
        read_only_fields = ["owner", "domain"] 

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class ApartmentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApartmentImages
        fields = "__all__"


class ApartmentSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    facilities = serializers.PrimaryKeyRelatedField(
        queryset=FacilityService.objects.all(),
        many=True,
        required=False,
        write_only=True
    )

    amenities = serializers.PrimaryKeyRelatedField(
        queryset=Amenity.objects.all(),
        many=True,
        required=False,
        write_only=True
    )

    images = ApartmentImageSerializer(many=True, read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Apartments
        fields = "__all__"

    def create(self, validated_data):
        request = self.context["request"]

        # Extract nested data
        address_data = validated_data.pop("address")
        amenities_data = validated_data.pop("amenities", [])
        facilities_data = validated_data.pop("facilities", [])

        # Create address
        address = Address.objects.create(**address_data)

        # Create apartment
        apartment = Apartments.objects.create(
            address=address,
            owner=request.user,
            **validated_data
        )

        # Set M2M
        apartment.amenities.set(amenities_data)
        apartment.facilities.set(facilities_data)

        # Handle image upload
        for key, file_obj in request.FILES.items():
            if key.startswith("images[") and ".image" in key:

                index = key.split("[")[1].split("]")[0]
                sequence = request.data.get(f"images[{index}].sequence", index)

                ApartmentImages.objects.create(
                    apartment=apartment,
                    image=file_obj,
                    sequence=sequence
                )

        return apartment

    def update(self, instance, validated_data):
        request = self.context["request"]

        # Extract nested fields
        address_data = validated_data.pop("address", None)
        amenities_data = validated_data.pop("amenities", None)
        facilities_data = validated_data.pop("facilities", None)

        # Update address
        if address_data:
            address_serializer = AddressSerializer(
                instance.address,
                data=address_data,
                partial=True
            )
            address_serializer.is_valid(raise_exception=True)
            address_serializer.save()

        # Update M2M fields
        if amenities_data is not None:
            instance.amenities.set(amenities_data)

        if facilities_data is not None:
            instance.facilities.set(facilities_data)

        # Update other simple fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # If new images uploaded → delete old + save new
        if request.FILES:
            instance.images.all().delete()

            for key, file_obj in request.FILES.items():
                if key.startswith("images[") and ".image" in key:
                    index = key.split("[")[1].split("]")[0]
                    sequence = request.data.get(f"images[{index}].sequence", index)

                    ApartmentImages.objects.create(
                        apartment=instance,
                        image=file_obj,
                        sequence=sequence
                    )

        return instance


class ApartmentDetailSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    facilities = FacilityServiceSerializer(many=True)
    amenities = AmenitySerializer(many=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    images = ApartmentImageSerializer(many=True, read_only=True)

    class Meta:
        model = Apartments
        fields = "__all__"
