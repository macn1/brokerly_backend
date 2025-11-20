from django.urls import path
from .views import (
    userRegisterAPIView,
    VendorRegisterAPIView,
    VendorLoginAPIView,
    UniversalLoginAPIView,
    VendorListAPi,
    VendorDetailUpdateDeleteAPIVIew
)


urlpatterns = [
    path("register/user", userRegisterAPIView.as_view()),
    
    path("vendor/listall-vendors", VendorListAPi.as_view()),
    path("vendor/listall-vendors/<int:pk>", VendorDetailUpdateDeleteAPIVIew.as_view()),
    
    
    path("register/vendor", VendorRegisterAPIView.as_view()),
    path("vendor/login", VendorLoginAPIView.as_view()),
    path("user/login", UniversalLoginAPIView.as_view()),


]
