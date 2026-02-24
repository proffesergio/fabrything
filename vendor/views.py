from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.db.models import Sum, Count
from django.contrib.auth import get_user_model

from .models import Vendor, VendorRegistration, VendorPayout
from .serializers import (
    VendorRegistrationSerializer,
    VendorApplicationListSerializer,
    VendorApplicationDetailSerializer,
    VendorSerializer,
    VendorPayoutSerializer,
    ApplicationStatusSerializer
)
from .permissions import IsPublicOrAdmin, IsVendorOrAdmin, IsApprovedVendor

User = get_user_model()


class VendorApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for vendor applications"""
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['business_name', 'user__email', 'phone', 'tax_id']
    ordering_fields = ['created_at', 'status', 'business_name']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['create', 'list']:
            # Public can create, admin can list
            if self.action == 'create':
                return [AllowAny()]
            return [IsAdminUser()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action == 'list':
            return VendorApplicationListSerializer
        if self.action in ['retrieve', 'update', 'partial_update']:
            return VendorApplicationDetailSerializer
        return VendorRegistrationSerializer

    def get_queryset(self):
        if self.action == 'list':
            return VendorRegistration.objects.all()
        return VendorRegistration.objects.all()

    def create(self, request, *args, **kwargs):
        # Allow public to submit application
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # If user is authenticated, link to user
            if request.user.is_authenticated:
                serializer.save(user=request.user)
            else:
                serializer.save()
            return Response(
                {'message': 'Application submitted successfully', 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        instance = serializer.save(reviewed_by=self.request.user)

        # If approving, create vendor profile
        if instance.status == 'approved' and not hasattr(instance.user, 'vendor'):
            Vendor.objects.create(
                user=instance.user,
                business_name=instance.business_name,
                business_address=instance.business_address,
                phone=instance.phone,
                tax_id=instance.tax_id,
                is_approved=True,
                approved_at=timezone.now()
            )
            # Update user role to vendor
            instance.user.role = 'vendor'
            instance.user.save()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a vendor application"""
        application = self.get_object()
        if application.status != 'pending':
            return Response(
                {'error': 'Application is not in pending status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        application.status = 'approved'
        application.admin_notes = request.data.get('notes', '')
        application.reviewed_by = request.user
        application.save()

        # Create vendor profile
        Vendor.objects.create(
            user=application.user,
            business_name=application.business_name,
            business_address=application.business_address,
            phone=application.phone,
            tax_id=application.tax_id,
            is_approved=True,
            approved_at=timezone.now()
        )

        # Update user role
        application.user.role = 'vendor'
        application.user.save()

        return Response({'message': 'Application approved successfully'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a vendor application"""
        application = self.get_object()
        if application.status not in ['pending', 'review']:
            return Response(
                {'error': 'Application cannot be rejected in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        application.status = 'rejected'
        application.admin_notes = request.data.get('notes', 'Application rejected')
        application.reviewed_by = request.user
        application.save()

        return Response({'message': 'Application rejected'})

    @action(detail=True, methods=['post'])
    def mark_review(self, request, pk=None):
        """Mark application as under review"""
        application = self.get_object()
        application.status = 'review'
        application.reviewed_by = request.user
        application.save()
        return Response({'message': 'Application marked as under review'})


class VendorProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for vendor profile management"""
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'list']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Vendor.objects.all()
        return Vendor.objects.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Only allow vendors to update their own profile (non-admin fields)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current vendor's profile"""
        try:
            vendor = request.user.vendor
            serializer = self.get_serializer(vendor)
            return Response(serializer.data)
        except Vendor.DoesNotExist:
            return Response(
                {'error': 'No vendor profile found'},
                status=status.HTTP_404_NOT_FOUND
            )


class VendorStatsViewSet(viewsets.ViewSet):
    """ViewSet for vendor dashboard statistics"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get dashboard metrics for vendor"""
        user = request.user

        # Admin sees different stats
        if user.is_staff or user.role == 'admin':
            total_vendors = Vendor.objects.count()
            pending_applications = VendorRegistration.objects.filter(status='pending').count()
            approved_vendors = Vendor.objects.filter(is_approved=True).count()
            total_payouts = VendorPayout.objects.aggregate(Sum('amount'))['amount__sum'] or 0

            return Response({
                'total_vendors': total_vendors,
                'pending_applications': pending_applications,
                'approved_vendors': approved_vendors,
                'total_payouts': float(total_payouts),
                'sales_by_month': [],
                'top_vendors': []
            })

        # Vendor stats
        try:
            vendor = user.vendor

            # Calculate stats
            total_orders = 0  # Would come from OrderServices
            total_products = 0  # Would come from ProductServices

            # Recent payouts
            recent_payouts = VendorPayout.objects.filter(vendor=vendor)[:5]
            payout_serializer = VendorPayoutSerializer(recent_payouts, many=True)

            return Response({
                'business_name': vendor.business_name,
                'total_sales': float(vendor.total_sales),
                'pending_payout': float(vendor.pending_payout),
                'commission_rate': float(vendor.commission_rate),
                'total_orders': total_orders,
                'total_products': total_products,
                'is_approved': vendor.is_approved,
                'recent_payouts': payout_serializer.data,
                'sales_by_month': [],  # Mock data for chart
                'recent_orders': []  # Mock data
            })
        except Vendor.DoesNotExist:
            return Response(
                {'error': 'No vendor profile found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ApplicationStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for users to check their own application status"""
    serializer_class = ApplicationStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VendorRegistration.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_status(self, request):
        """Get current user's application status"""
        applications = VendorRegistration.objects.filter(user=request.user).order_by('-created_at')
        if applications.exists():
            latest = applications.first()
            serializer = self.get_serializer(latest)
            return Response(serializer.data)
        return Response({'message': 'No application found', 'has_application': False})
