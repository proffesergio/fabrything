from rest_framework import permissions


class IsPublicOrAdmin(permissions.BasePermission):
    """
    Allow public POST requests (for submitting applications).
    Admin users get full access.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True  # Public can submit applications
        if request.user and request.user.is_authenticated:
            return request.user.is_staff or request.user.role == 'admin'
        return False


class IsVendorOrAdmin(permissions.BasePermission):
    """
    Vendor users can read their own data.
    Admin users can read all.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # Admin can access all
        if request.user.is_staff or request.user.role == 'admin':
            return True
        # Vendor can only access their own objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'vendor'):
            return obj.vendor.user == request.user
        return False


class IsApprovedVendor(permissions.BasePermission):
    """
    Only approved vendors can access certain endpoints.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin always has access
        if request.user.is_staff or request.user.role == 'admin':
            return True

        # Check if user has a vendor profile and is approved
        if hasattr(request.user, 'vendor'):
            return request.user.vendor.is_approved

        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners to edit their objects.
    """
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_staff or request.user.role == 'admin':
            return True

        # Check if the object has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'vendor') and hasattr(obj.vendor, 'user'):
            return obj.vendor.user == request.user

        return False
