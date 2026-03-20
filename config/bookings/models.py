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
    vendor_name = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lead_requests",
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)

    apartment = models.ForeignKey(
        Apartments, on_delete=models.CASCADE, related_name="leads"
    )

    message = models.TextField()
    request_status = models.CharField(
        max_length=50, choices=LEAD_STATUS_CHOICES, default="Requested"
    )
    request_mode = models.CharField(
        max_length=10, choices=REQUEST_MODE_CHOICES, default="Online"
    )

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} → {self.apartment.name}"


VISIT_STATUS_CHOICES = (
    ("Interested", "Interested"),
    ("Rejected", "Rejected"),
    ("Holding", "Holding"),
    ("Booked", "Booked"),
    ("Paid", "Paid"),
)


class LeadVisit(models.Model):
    lead = models.ForeignKey(
        LeadRequest, on_delete=models.CASCADE, related_name="visits"
    )

    visit_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=30, choices=VISIT_STATUS_CHOICES, default="Interested"
    )

    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Visit for {self.lead.name} - {self.status}"


class VendorTransaction(models.Model):
    vendor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    apartment = models.ForeignKey(
        Apartments, on_delete=models.CASCADE, related_name="transactions"
    )
    lead_visit = models.OneToOneField(
        "LeadVisit",  # same app, no need for 'crm.LeadVisit'
        on_delete=models.CASCADE,
        related_name="transaction",
        null=True,
        blank=True,
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor} | {self.apartment} | paid={self.amount_paid}"
