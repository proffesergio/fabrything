from django.contrib import admin
from .models import Vendor, VendorRegistration, VendorPayout


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'phone', 'is_approved', 'commission_rate', 'total_sales', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['business_name', 'user__email', 'phone', 'tax_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'business_name', 'business_address', 'phone', 'tax_id')
        }),
        ('Approval Status', {
            'fields': ('is_approved', 'approved_at')
        }),
        ('Financial', {
            'fields': ('commission_rate', 'total_sales', 'pending_payout')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(VendorRegistration)
class VendorRegistrationAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'business_type', 'phone', 'status', 'created_at']
    list_filter = ['status', 'business_type', 'created_at']
    search_fields = ['business_name', 'user__email', 'phone', 'tax_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Business Details', {
            'fields': ('business_name', 'business_type', 'business_address', 'phone', 'tax_id')
        }),
        ('Documents', {
            'fields': ('nid_document', 'trade_license', 'tin_certificate')
        }),
        ('Payout Details', {
            'fields': ('payout_method', 'payout_account')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes', 'reviewed_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    actions = ['approve_applications', 'reject_applications']

    def approve_applications(self, request, queryset):
        for application in queryset.filter(status='pending'):
            application.status = 'approved'
            application.admin_notes = 'Bulk approved'
            application.reviewed_by = request.user
            application.save()
        self.message_user(request, f"{queryset.count()} applications approved.")

    def reject_applications(self, request, queryset):
        for application in queryset.filter(status__in=['pending', 'review']):
            application.status = 'rejected'
            application.admin_notes = 'Bulk rejected'
            application.reviewed_by = request.user
            application.save()
        self.message_user(request, f"{queryset.count()} applications rejected.")


@admin.register(VendorPayout)
class VendorPayoutAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'amount', 'method', 'status', 'transaction_id', 'created_at']
    list_filter = ['status', 'method', 'created_at']
    search_fields = ['vendor__business_name', 'transaction_id']
    readonly_fields = ['created_at', 'processed_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Vendor Information', {
            'fields': ('vendor',)
        }),
        ('Payout Details', {
            'fields': ('amount', 'method', 'transaction_id')
        }),
        ('Status', {
            'fields': ('status', 'processed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
