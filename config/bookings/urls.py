from django.contrib import admin
from django.urls import path, include
from .views import (
    LeadCreateAPIView,
    PaginatedLeadPageapi,
    PaginatedLeadPageapiVendor,
    ReadUpdateDeleleLeads,
    LeadVisitListCreateAPIView,
    AllbokingsDomainApiView,
    AllbookingsApiView,
    VendorTransactionSummaryView
)

urlpatterns = [
    path("lead-generation", LeadCreateAPIView.as_view()),
    path("all-leads", PaginatedLeadPageapi.as_view()),
    path("all-bookings", AllbookingsApiView.as_view()),
    path("all-leads/<int:pk>", ReadUpdateDeleleLeads.as_view()),
    path("vendor-all-leads", PaginatedLeadPageapiVendor.as_view()),
    path("vendor-all-bookings", AllbokingsDomainApiView.as_view()),
    path("lead-visit", LeadVisitListCreateAPIView.as_view()),
    path("vendor-transactions", VendorTransactionSummaryView.as_view()),  # add this

]
