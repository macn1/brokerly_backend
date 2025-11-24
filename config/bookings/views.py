from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.models import User
from apartments.models import Apartments
from .models import LeadRequest
from .serializer import LeadRequestSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from permissoins.super_permissions import IsDomainAdmin
from django.shortcuts import get_object_or_404
from rest_framework import status
class LeadCreateAPIView(APIView):

    def post(self, request):
        data = request.data.copy()
        email = data.get("email")
        name = data.get("name")
        mobile = data.get("mobile")

        if not email:
            return Response({"error": "Email is required"}, status=400)
        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create_user(
                name=name,
                email=email,
                phone_number=mobile,
                password=None,   
                role="User"
            )
        data["user"] = user.id

        serializer = LeadRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Lead submitted successfully", "data": serializer.data},
                status=201
            )
        return Response(serializer.errors, status=400)

class PaginatedLeadPageapi(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        leads = LeadRequest.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size=10
        result_page = paginator.paginate_queryset(leads,request)
        serializer = LeadRequestSerializer(result_page,many=True)
        return paginator.get_paginated_response(serializer.data)
    


class PaginatedLeadPageapiVendor(APIView):
    permission_classes = [IsAuthenticated, IsDomainAdmin]

    def get(self, request):
        domain = request.domain  
        leads = LeadRequest.objects.filter(apartment__domain=domain)

        print('leads',leads)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(leads, request)

        serializer = LeadRequestSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class ReadUpdateDeleleLeads(APIView):
    permission_classes=[IsAuthenticated]
    
    def get (self,request,pk):
        leads = get_object_or_404(LeadRequest,pk=pk)
        serialzier = LeadRequestSerializer(leads)
        return Response(serialzier.data,status=status.HTTP_200_OK)
    
    def delete(self,request,pk):
        leads = get_object_or_404(LeadRequest,pk=pk)
        leads.delete()
        return Response({"message","item deteted"},status=status.HTTP_204_NO_CONTENT)