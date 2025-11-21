from rest_framework import serializers
from .models import User, VendorProfile, Domain,MemberProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class MemberSerializer(serializers.ModelSerializer):
    designation = serializers.CharField(source="member_profile.designation", required=False)
    
    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'email',
            'phone_number',
            'designation',
            'password',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        profile_data = validated_data.pop("member_profile", {})
        request = self.context["request"]

        member = User.objects.create_member(
            name=validated_data["name"],
            email=validated_data["email"],
            password=validated_data.get("password"),
            phone_number=validated_data.get("phone_number"),
            domain=request.domain 
        )

        # Create MemberProfile
        MemberProfile.objects.create(
            user=member,
            designation=profile_data.get("designation"),
            domain=request.domain 
        )

        return member


# -------------------------------
# User Registration Serializer
# -------------------------------
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'password']

    def create(self, validated_data):
        validated_data['role'] = 'User'
        return User.objects.create_user(**validated_data)


class VendorListSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(source='domain.name', read_only=True)
    favicon = serializers.CharField(source='domain.favicon', read_only=True)
    logo = serializers.CharField(source='domain.logo', read_only=True)

    
    vendor_address = serializers.CharField(source='vendor_profile.address', read_only=True)
    vendor_status = serializers.CharField(source='vendor_profile.vendor_status', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone_number', 'domain', 'vendor_address', 'vendor_status', 'created_at','favicon','logo']


class VendorRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    address = serializers.CharField(write_only=True)
    vendor_status = serializers.ChoiceField(
        write_only=True,
        choices=[("Pending","Pending"), ("Approved","Approved"), ("Rejected","Rejected")],
        default="Pending"
    )

    # Domain fields
    domain_name = serializers.CharField(write_only=True)
    domain_favicon = serializers.ImageField(write_only=True, required=False, allow_null=True)
    domain_logo = serializers.ImageField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'name', 'email', 'phone_number', 'password',
            'address', 'vendor_status',
            'domain_name', 'domain_favicon', 'domain_logo'
        ]

    def validate_domain_name(self, value):
        if not value:
            raise serializers.ValidationError("Domain name is required")
        return value

    def create(self, validated_data):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Validated data: {validated_data}")


        # Extract domain and address fields
        domain_name = validated_data.pop('domain_name')
        domain_favicon = validated_data.pop('domain_favicon', None)
        domain_logo = validated_data.pop('domain_logo', None)
        address = validated_data.pop('address')
        vendor_status = validated_data.pop('vendor_status', 'Pending')  # safe default

        # Get or create domain
        domain, created = Domain.objects.get_or_create(
            name=domain_name,
            defaults={'favicon': domain_favicon, 'logo': domain_logo}
        )

        # Update existing domain images if provided
        if not created:
            updated = False
            if domain_favicon:
                domain.favicon = domain_favicon
                updated = True
            if domain_logo:
                domain.logo = domain_logo
                updated = True
            if updated:
                domain.save()

        # Create User as vendor
        validated_data['role'] = 'Vendor'
        user = User.objects.create_vendor(
            domain=domain,
            **validated_data
        )

        # Create VendorProfile (no vendor_status here)
        VendorProfile.objects.create(
            user=user,
            domain=domain,
            vendor_status=vendor_status,
            address=address
        )

        return user


# -------------------------------
# Vendor Login Serializer
# -------------------------------
class VendorLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        if user.role != "Vendor":
            raise serializers.ValidationError("This account is not a vendor")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "phone_number": user.phone_number,
                "domain": user.domain.name if user.domain else None,
                "vendor_address": user.vendor_profile.address if hasattr(user, 'vendor_profile') else None,
                "vendor_status": user.vendor_profile.vendor_status if hasattr(user, 'vendor_profile') else None,
            }
        }


# -------------------------------
# Universal Login Serializer (for all roles)
# -------------------------------
class UniversalLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "phone_number": user.phone_number,
                "domain": user.domain.name if user.domain else None,
                "vendor_address": user.vendor_profile.address if hasattr(user, 'vendor_profile') else None,
                "vendor_status": user.vendor_profile.vendor_status if hasattr(user, 'vendor_profile') else None,
            }
        }


# -------------------------------
# Custom JWT Token Serializer
# -------------------------------
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'name': self.user.name,
            'role': self.user.role,
            'phone_number': self.user.phone_number,
            'domain': self.user.domain.name if self.user.domain else None,
            'vendor_address': self.user.vendor_profile.address if hasattr(self.user, 'vendor_profile') else None,
            'vendor_status': self.user.vendor_profile.vendor_status if hasattr(self.user, 'vendor_profile') else None,
        }
        return data
