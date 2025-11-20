

from django.contrib import admin
from django.urls import path,include
from .views import AmenityListCreateAPIView,AmenityDetailUpdateDelete,FacilityCreateListApiView,PaginatedFacilityAPIView,FacilityDetailCreateDelete,ApartmentListCreateAPIView,ApartmentDetailupdateAPIView

urlpatterns = [
    path('amenity',AmenityListCreateAPIView.as_view()),
    path('amenity/<int:pk>',AmenityDetailUpdateDelete.as_view(),name='amenity'),
    path('facility/<int:pk>',FacilityDetailCreateDelete.as_view()),
    path('facility',FacilityCreateListApiView.as_view()),
    path('paginated-facility',PaginatedFacilityAPIView.as_view()),
     path('apartment',ApartmentListCreateAPIView.as_view(),name='apartment'),
     path('apartment/<int:pk>',ApartmentDetailupdateAPIView.as_view(),name='apartment'),
]
