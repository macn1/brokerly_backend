from django.urls import path
from .views import (
    userRegisterAPIView,
    VendorRegisterAPIView,
    VendorLoginAPIView,
    UniversalLoginAPIView,
    VendorListAPi,
    VendorDetailUpdateDeleteAPIVIew,
    MemberCreateAPIView,
    MemberReadUpdateDeleteApi
)


urlpatterns = [
    path("register/user", userRegisterAPIView.as_view()),
    path("register/member", MemberCreateAPIView.as_view()),
    path("register/vendor", VendorRegisterAPIView.as_view()),
    
    
    path("vendor/listall-vendors", VendorListAPi.as_view()),
    path("vendor/listall-members", MemberCreateAPIView.as_view()),
    
    path("vendor/listall-vendors/<int:pk>", VendorDetailUpdateDeleteAPIVIew.as_view()),
    path("vendor/listall-members/<int:pk>", MemberReadUpdateDeleteApi.as_view()),
    
    
    
    path("vendor/login", VendorLoginAPIView.as_view()),
    path("user/login", UniversalLoginAPIView.as_view()),


]
