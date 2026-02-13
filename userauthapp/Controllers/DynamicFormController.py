from django.apps import apps
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from userauthapp.models import User
from rest_framework.views import APIView
from fabrythingapp.Helpers import getDynamicModels, getDynamicFormFields

class DynamicFormController(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, modelName=None):
        if modelName not in getDynamicModels():
            return Response(
                {'error': 'modelName parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model = getDynamicModels()[modelName]
        model_class = apps.get_model(model)

        if model_class is None:
            return Response(
                {'error': f'Model "{modelName}" not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        model_instance = model_class()
        fields = getDynamicFormFields(model_instance, request.user.domain_user_id)
        return Response(
            {
                'data':fields,
                'message': f'Form structure for {modelName} retrieved successfully'
            }
        )       
        # Example dynamic form structure
        form_structure = {
            "fields": [
                {"name": "first_name", "type": "text", "label": "First Name", "required": True},
                {"name": "last_name", "type": "text", "label": "Last Name", "required": True},
                {"name": "email", "type": "email", "label": "Email Address", "required": True},
                {"name": "age", "type": "number", "label": "Age", "required": False},
            ],
            "submit_url": "/api/v1/submit-form/"
        }
        return Response(form_structure, status=status.HTTP_200_OK)
    