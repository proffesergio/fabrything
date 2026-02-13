from django.db.models import FileField, ImageField, ForeignKey

def getDynamicModels():
    return {
        'product': 'ProductServices.Products',
        'category': 'ProductServices.Categories',
        'warehouse': 'InventoryServices.Warehouse',
    }

def checkisFileField(field):
    return field in ['image',
                     'file',
                     'document',
                     'photo',
                     'attachment',
                     'video',
                     'audio',
                     'pdf',]

def getExcludeField():
    return ['id', 'created_at', 'updated_at', 'domain_user_id', 'created_by_user_id', 'updated_by_user_id']

def getDynamicFormFields(model_instance, domain_user_id):
    fields = {'text': [], 'select': [], 'checkbox': [], 'radio': [], 'textarea': [], 'json': [], 'file': []}
    for field in model_instance._meta.fields:
        if field.name in getExcludeField():
            continue
        label = field.name.replace('_',' ').title()
        fielddata={
            'name':field.name,
            'label':field.verbose_name,
            'placeholder': 'Enter '+label,
            'default': model_instance.__dict__[field.name] if field.name in model_instance.__dict__ else '',
            'required': not field.null,

        }
        if checkisFileField(field.name):
            fielddata['type'] = 'file'
            fields['file'].append(fielddata)
            continue
        elif field.get_internal_type() == 'TextField':
            fielddata['type'] = 'textarea'
        elif field.get_internal_type() == 'JSONField':
            fielddata['type'] ='json'
        elif field.get_internal_type() == 'CharField' and field.choices:
            fielddata['type'] = 'select'
            fielddata['options'] = [{'value': choice[0], 'display': choice[1]} for choice in field.choices]
        elif field.get_internal_type() == 'CharField' or field.get_internal_type() == 'IntegerField' or field.get_internal_type()=='DecimalField' or field.get_internal_type() == 'FloatField':
            fielddata['type'] = 'text'
        elif field.get_internal_type() == 'BooleanField' or field.get_internal_type() == 'NullBooleanField':
            fielddata['type'] = 'checkbox'
        else:
            fielddata['type'] = 'text'  # Default to text for unsupported field types
            if isinstance(field, ForeignKey):
                related_model=field.related_model
                related_key=field.name
                related_key_name=''

                if hasattr(related_model, 'defaultkey'):
                    related_key_name=related_model.defaultkey()
                    options=related_model.objects.filter(domain_user_id).values_list('id', related_key_name, related_model.getDefaultkey())
                else:
                    related_key_name = related_model._meta.pk.name
                    options = related_model.objects.filter(domain_user_id = domain_user_id).values_list('id', related_key_name, 'name')

                fielddata['options'] = [{'id':option[0], 'value':option[1]} for option in options]
            fielddata['type'] = 'select'
                
        fields[fielddata['type']].append(fielddata)
    return fields