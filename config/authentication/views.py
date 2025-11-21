from django.shortcuts import render
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import (
    UserRegisterSerializer,
    MyTokenObtainPairSerializer,
    VendorRegisterSerializer,
    VendorLoginSerializer,
    UniversalLoginSerializer,
    VendorListSerializer,
    MemberSerializer
)
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from permissoins.super_permissions import IsDomainAdmin

from django.shortcuts import get_object_or_404


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MemberCreateAPIView(APIView):
    permission_classes = [IsAuthenticated,IsDomainAdmin]

    def post(self, request):
        serializer = MemberSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            member = serializer.save()
            return Response(
                {"message": "Member created successfully", "member": serializer.data},
                status=201,
            )
        return Response(serializer.errors, status=400)
    
    def get(self,request):
        users = User.objects.filter(role='Member').order_by('created_at')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(users,request)
        serializer = MemberSerializer(result_page,many=True)
        return paginator.get_paginated_response(serializer.data)

class MemberReadUpdateDeleteApi(APIView):
    permission_classes=[IsAuthenticated,IsDomainAdmin]
    def get(self,request,pk):
        user = get_object_or_404(User,pk=pk)
        serializer = MemberSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response({"message": f"{user.name} item deleted"})

class VendorListAPi(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        users = User.objects.filter(role="Vendor").order_by("created_at")
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(users, request)
        serializer = VendorListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class VendorDetailUpdateDeleteAPIVIew(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk):
        vendor = get_object_or_404(User, pk=pk)
        serialzer = VendorListSerializer(vendor)
        return Response(serialzer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        vendor = get_object_or_404(User, pk=pk)
        vendor.delete()
        return Response({"message": f"{vendor.name} item deleted"})


class VendorRegisterAPIView(APIView):
    def post(self, request):
        serializer = VendorRegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Vendor Created Successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"status": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class VendorLoginAPIView(APIView):
    def post(self, request):
        serializer = VendorLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class userRegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User Created Successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UniversalLoginAPIView(APIView):
    def post(self, request):
        serializer = UniversalLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
