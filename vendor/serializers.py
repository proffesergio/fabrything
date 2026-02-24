from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Vendor, VendorRegistration, VendorPayout

User = get_user_model()


class VendorRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for submitting vendor applications"""
    class Meta:
        model = VendorRegistration
        fields = [
            'id', 'business_name', 'business_type', 'business_address',
            'phone', 'tax_id', 'nid_document', 'trade_license',
            'tin_certificate', 'payout_method', 'payout_account',
            'status', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class VendorApplicationListSerializer(serializers.ModelSerializer):
    """Serializer for admin list view of applications"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = VendorRegistration
        fields = [
            'id', 'user_email', 'user_name', 'business_name', 'business_type',
            'phone', 'tax_id', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = fields

    def get_user_name(self, obj):
        return obj.user.name or obj.user.username


class VendorApplicationDetailSerializer(serializers.ModelSerializer):
    """Serializer for admin detail/approval view"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = VendorRegistration
        fields = [
            'id', 'user_email', 'user_name', 'business_name', 'business_type',
            'business_address', 'phone', 'tax_id',
            'nid_document', 'trade_license', 'tin_certificate',
            'payout_method', 'payout_account',
            'status', 'admin_notes', 'reviewed_by', 'reviewed_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'user_name', 'created_at', 'updated_at',
            'reviewed_by_name'
        ]

    def get_user_name(self, obj):
        return obj.user.name or obj.user.username

    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.name or obj.reviewed_by.email
        return None


class VendorSerializer(serializers.ModelSerializer):
    """Serializer for vendor profile"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = [
            'id', 'user_email', 'user_name', 'business_name', 'business_address',
            'phone', 'tax_id', 'is_approved', 'approved_at', 'commission_rate',
            'total_sales', 'pending_payout', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'user_name', 'is_approved', 'approved_at',
            'total_sales', 'pending_payout', 'created_at', 'updated_at'
        ]

    def get_user_name(self, obj):
        return obj.user.name or obj.user.username


class VendorPayoutSerializer(serializers.ModelSerializer):
    """Serializer for payout records"""
    vendor_name = serializers.CharField(source='vendor.business_name', read_only=True)

    class Meta:
        model = VendorPayout
        fields = [
            'id', 'vendor_name', 'amount', 'method', 'status',
            'transaction_id', 'created_at', 'processed_at'
        ]
        read_only_fields = ['id', 'vendor_name', 'created_at']


class ApplicationStatusSerializer(serializers.ModelSerializer):
    """Serializer for checking own application status"""
    class Meta:
        model = VendorRegistration
        fields = [
            'id', 'business_name', 'status', 'admin_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
