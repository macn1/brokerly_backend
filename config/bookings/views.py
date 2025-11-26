from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.models import User
from apartments.models import Apartments
from .models import LeadRequest,LeadVisit
from .serializer import LeadRequestSerializer,LeadVisitSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from permissoins.super_permissions import IsDomainAdmin
from django.shortcuts import get_object_or_404
from rest_framework import status



class LeadVisitListCreateAPIView(APIView):

    def get(self, request):
        visits = LeadVisit.objects.all().order_by('-visit_date')
        serializer = LeadVisitSerializer(visits, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        vendor_id = request.data.get("vendor_name")
        lead_id = request.data.get("lead")

        serializer = LeadVisitSerializer(data=request.data)
        if serializer.is_valid():
            if vendor_id:
                lead = LeadRequest.objects.get(id=lead_id)

                if lead.vendor_name is None:
                    vendor = User.objects.get(id=vendor_id)
                    lead.vendor_name = vendor
                    lead.save()

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




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


