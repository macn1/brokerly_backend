from django.db import models
from authentication.models import User,Domain
from datetime import time


ROOM_TYPES = [("1BHK", "1BHK"), ("2BHK", "2BHK"), ("3BHK", "3BHK")]
APARTMENT_STATUS_CHOICES = (
    ("Pending", "Pending"),
    ("Approved", "Approved"),
    ("Rejected", "Rejected"),
)
BOOKING_STATUS_CHOICES = (
    ("Pending", "Pending"),         # user requested, waiting for review
    ("Confirmed", "Confirmed"),     # approved & booked
    ("Cancelled", "Cancelled"),     # cancelled by user/admin
    ("CheckedIn", "Checked In"),    # user has arrived
    ("CheckedOut", "Checked Out"),  # user has left
    ("Completed", "Completed"),     # booking full lifecycle completed
)


class Address(models.Model):
    address_line = models.TextField()
    city = models.CharField(max_length=200)
    pincode = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=200)
    country = models.CharField(max_length=100)


class Category(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategory",
    )


class Amenity(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="amenities")
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="amenities/", blank=True, null=True)



class FacilityService(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="facility_services")
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name="amenities")
    SERVICE_TYPE_CHOICES = [
        ("included", "Included"),
        ("additional", "Additional"),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)






class Apartments(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50,choices=APARTMENT_STATUS_CHOICES,default="Pending")
    availability = models.CharField(max_length=50,choices=BOOKING_STATUS_CHOICES,default='Pending')
    domain = models.ForeignKey(
        Domain,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="apartments")
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name="apartments"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="apartments",blank=True,null=True
    )
    amenities = models.ManyToManyField(Amenity, blank=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    price = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    facilities = models.ManyToManyField(
        FacilityService, related_name="apartment_facility", blank=True
    )
 

class ApartmentImages(models.Model):
    apartment = models.ForeignKey(
        Apartments, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="apartment/images", null=True, blank=True)
    sequence = models.TextField(max_length=20, default="1")


