from rest_framework.exceptions import APIException as DRFAPIException
import logging

logger = logging.getLogger(__name__)

class APIException(DRFAPIException):
    """Base API Exception"""
    status_code = 400
    default_detail = 'An error occurred'
    default_code = 'error'

class ValidationError(APIException):
    status_code = 400
    default_detail = 'Validation failed'
    default_code = 'validation_error'

class NotFoundError(APIException):
    status_code = 404
    default_detail = 'Resource not found'
    default_code = 'not_found'

class UnauthorizedError(APIException):
    status_code = 401
    default_detail = 'Unauthorized'
    default_code = 'unauthorized'

class PermissionError(APIException):
    status_code = 403
    default_detail = 'Permission denied'
    default_code = 'permission_denied'

class ConflictError(APIException):
    status_code = 409
    default_detail = 'Conflict'
    default_code = 'conflict'