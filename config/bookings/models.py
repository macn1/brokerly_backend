from django.db import models
from authentication.models import User
from apartments.models import Apartments

LEAD_STATUS_CHOICES = (
    ("Requested", "Requested"),
    ("Approved", "Approved"),
    ("Holding", "Holding"),
    ("Rejected", "Rejected"),
)
REQUEST_MODE_CHOICES = (
    ("Online", "Online"),
    ("Offline", "Offline"),
)

class LeadRequest(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lead_requests"
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)

    apartment = models.ForeignKey(
        Apartments,
        on_delete=models.CASCADE,
        related_name="leads"
    )

    message = models.TextField()
    request_status = models.CharField(
        max_length=50,
        choices=LEAD_STATUS_CHOICES,
        default="Requested"
    )
    request_mode = models.CharField(
        max_length=10,
        choices=REQUEST_MODE_CHOICES,
        default="Online"
    )
    
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} → {self.apartment.name}"
