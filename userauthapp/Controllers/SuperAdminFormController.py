from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.apps import apps
from fabrythingapp.Helpers import getExcludeField, getSuperAdminFormModels, renderResponse
from fabrythingapp.Permission import IsSuperAdmin
from django.core.serializers import serialize
import json

class SuperAdminDynamicFormController(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        return renderResponse(
            data='You are a Super Admin!',
            message='Success',
            status=200
        )
    
    def post(self, request, modelName):
        # Checking if Model exists in DynamicForm Models
        if modelName not in getSuperAdminFormModels():
            return renderResponse(
                data=f'Model "{modelName}" not found',
                message='Error',
                status=404
            )
        #Getting the Model Name from Dynamic Form Models
        model = getSuperAdminFormModels()[modelName]
        model_class = apps.get_model(model)

        #Check if Model Class Exists
        if model_class is None:
            return renderResponse(
                data=f'Model "{modelName}" not found',
                message='Error',
                status=404
            )
        # Getting Model Fields Info
        fields_info = model_class._meta.fields
        # Getting Model Fields Name
        model_field = {field.name: field for field in fields_info}
        # Getting the excluded Fields
        exclude_fields = getExcludeField()

        # Checking the Required Fields are in the Model Data
        required_fields = [field.name for field in fields_info if not field.null and not field.blank and field.name not in exclude_fields]

        # Matchin with validation for fields not exist in Post Data
        missing_fields = [field for field in required_fields if field not in request.data]
        # If Missing Fields Exist
        if missing_fields:
            return renderResponse(
                data=f'Missing required fields: {", ".join(missing_fields)}',
                message='Error',
                status=400
            )
        # Creating a copy of Post Data for Manipulation
        fields = request.data.copy()

        
        # Filtering the Post Data Fields by Model Fields and Eliminating the Extra Fields
        fieldsdata = { key:value for key, value in fields.items() if key in model_field and key not in exclude_fields}
        # All Model Fields Data 
        print(model_field)

        # All the Post Data Fields
        print(fieldsdata.items())
        # Sanitizing Foreign key instance for FK Fields in the Post Data
        for field in fields_info:
            if field.is_relation and field.name in fieldsdata and isinstance(fieldsdata[field.name], int):
                try:
                    related_instance = field.related_model.objects.get(id=fieldsdata[field.name])
                    fieldsdata[field.name] = related_instance
                except field.related_model.DoesNotExist:
                    return renderResponse(
                        data=f'Related instance with id {fieldsdata[field.name]} not found for field "{field.name}"',
                        message='Error',
                        status=400
                        )
        # Creating the Model Instance with the Sanitized Data and Saving to Database
        model_instance = model_class.objects.create(**fieldsdata)
        model_instance.save()
        return renderResponse(
                data=f'{modelName} created successfully with id {model_instance.id}',
                message='Success',
                status=201
            )            
        # Serializing Data
        serialized_data = serialize('json', [model_instance])
        # Converting Serialized Data to Json
        model_json = json.loads(serialized_data)
        # Getting the first object of the Json
        response_json = model_json[0]['fields']
        response_json['id'] = model_json[0]['pk']
        # Returning the Response
        return renserResponse(
            data = response_json,
            message = 'Data saved successfully'
        )
    