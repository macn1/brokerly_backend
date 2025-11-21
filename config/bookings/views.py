from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.models import User
from apartments.models import Apartments
from .models import LeadRequest
from .serializers import LeadRequestSerializer

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

        # Step 3: Save lead
        serializer = LeadRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Lead submitted successfully", "data": serializer.data},
                status=201
            )

        return Response(serializer.errors, status=400)
