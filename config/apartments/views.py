from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Amenity ,FacilityService,Apartments
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from .serializer import AmenitySerializer,FacilityServiceSerializer,ApartmentSerializer,ApartmentDetailSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import get_object_or_404
from permissoins.super_permissions import IsDomainAdmin



class ApartmentListCreateAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ApartmentSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        apartments = (
            Apartments.objects.select_related("address", "owner")
            .prefetch_related( "facilities", "amenities", "images")
            .order_by("id")
        )
        serializer = ApartmentDetailSerializer(apartments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApartmentDetailupdateAPIView(APIView):
    def get(self, request, pk):
        apartment = get_object_or_404(Apartments, pk=pk)
        serializer = ApartmentDetailSerializer(apartment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        apartment = get_object_or_404(Apartments, pk=pk)
        apartment.delete()
        return Response({"message": "Apartment deleted"})

    def put(self, request, pk):
        return self.update_apartment(request, pk, partial=False)

    def patch(self, request, pk):
        return self.update_apartment(request, pk, partial=True)

    def update_apartment(self, request, pk, partial=False):
        apartment = get_object_or_404(Apartments, pk=pk)

        # Check ownership before update
        if apartment.owner != request.user:
            return Response(
                {"error": "You don't have permission to edit this apartment"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ApartmentSerializer(
            apartment, data=request.data, partial=partial, context={"request": request}
        )

        if serializer.is_valid():
            try:
                # Update the apartment
                updated_apartment = serializer.save()

                # Return the updated apartment with full details
                detail_serializer = ApartmentDetailSerializer(updated_apartment)
                return Response(
                    {
                        "message": "Apartment updated successfully",
                        "data": detail_serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                return Response(
                    {"error": f"Error updating apartment: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacilityCreateListApiView(APIView):
    permission_classes = [IsAuthenticated,IsDomainAdmin]

    def post(self, request):
        serializer = FacilityService(data=request.data)
        if serializer.is_valid():
            serializer.save(
                owner=request.user,
                domain=request.domain  
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
            facilities = FacilityService.objects.filter(
            owner=request.user,
            domain=request.user.domain)   
            serializer = FacilityServiceSerializer(facilities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

class PaginatedFacilityAPIView(APIView):
    permission_classes = [IsAuthenticated,IsDomainAdmin]
    def get(self, request):
        domain = request.domain  
        amenities = FacilityService.objects.filter(domain=domain)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(amenities, request)
        serializer = FacilityServiceSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class FacilityDetailCreateDelete(APIView):
    permission_classes = [IsAuthenticated,IsDomainAdmin]

    def get_object(self, pk, user):
        return get_object_or_404(FacilityService, pk=pk, owner=user)

    def get(self, request, pk):
        facility = self.get_object(pk, request.user)
        serializer = FacilityServiceSerializer(facility)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        facility = self.get_object(pk, request.user)
        serializer = FacilityServiceSerializer(
            facility, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save(owner=request.user)  # ensure owner stays same
            return Response(
                {"message": "Facility updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        facility = self.get_object(pk, request.user)
        facility.delete()
        return Response({"message": "Facility deleted successfully"}, status=status.HTTP_200_OK)




# class AmenityListCreateAPIView(APIView):
    
#     permission_classes = [IsAuthenticated,IsDomainAdmin]  
#     def post(self, request):
#         serializer = AmenitySerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(
#                 owner=request.user,
#                 domain=request.domain  
#             )
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def get(self, request):
#         domain = request.domain  
#         amenities = Amenity.objects.filter(domain=domain)
#         paginator = PageNumberPagination()
#         paginator.page_size = 10
#         result_page = paginator.paginate_queryset(amenities, request)
#         serializer = AmenitySerializer(result_page, many=True)
#         return paginator.get_paginated_response(serializer.data)

class AmenityListCreateAPIView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(),AllowAny()]          
        elif self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]  
        return super().get_permissions()

    def get(self, request):
        amenities = Amenity.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(amenities, request)
        serializer = AmenitySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AmenitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)



class AmenityDetailUpdateDelete(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        if user.is_admin:  # admin can access any
            return get_object_or_404(Amenity, pk=pk)
        return get_object_or_404(Amenity, pk=pk, owner=user)

    def get(self, request, pk):
        amenity = self.get_object(pk, request.user)
        serializer = AmenitySerializer(amenity)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        amenity = self.get_object(pk, request.user)
        serializer = AmenitySerializer(amenity, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(
                {"message": "Amenity Updated", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        amenity = self.get_object(pk, request.user)
        amenity.delete()
        return Response({"message": "Amenity deleted"}, status=status.HTTP_200_OK)
