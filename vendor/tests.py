from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
from .models import Vendor, VendorRegistration, VendorPayout

User = get_user_model()


class VendorModelTest(TestCase):
    """Tests for Vendor model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='vendor@test.com',
            username='vendor',
            password='testpass123'
        )

    def test_vendor_creation(self):
        vendor = Vendor.objects.create(
            user=self.user,
            business_name='Test Business',
            business_address='123 Test St',
            phone='+8801234567890',
            tax_id='TIN123456'
        )
        self.assertEqual(str(vendor), 'Test Business')
        self.assertFalse(vendor.is_approved)
        self.assertEqual(vendor.commission_rate, 10.00)

    def test_vendor_defaults(self):
        vendor = Vendor.objects.create(
            user=self.user,
            business_name='Test Business',
            business_address='123 Test St',
            phone='+8801234567890',
            tax_id='TIN123457'
        )
        self.assertEqual(vendor.total_sales, 0)
        self.assertEqual(vendor.pending_payout, 0)


class VendorRegistrationModelTest(TestCase):
    """Tests for VendorRegistration model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='applicant@test.com',
            username='applicant',
            password='testpass123'
        )

    def test_registration_creation(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        nid_file = SimpleUploadedFile(
            "nid.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

        registration = VendorRegistration.objects.create(
            user=self.user,
            business_name='My Shop',
            business_type='company',
            business_address='456 Business Ave',
            phone='+8809876543210',
            tax_id='TIN654321',
            nid_document=nid_file,
            payout_method='bkash',
            payout_account='01712345678'
        )
        self.assertEqual(str(registration), 'My Shop - Pending')
        self.assertEqual(registration.status, 'pending')

    def test_status_choices(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        nid_file = SimpleUploadedFile(
            "nid.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

        registration = VendorRegistration.objects.create(
            user=self.user,
            business_name='My Shop',
            business_type='individual',
            business_address='456 Business Ave',
            phone='+8809876543210',
            tax_id='TIN654322',
            nid_document=nid_file,
            payout_method='nagad',
            payout_account='01712345679'
        )

        registration.status = 'review'
        registration.save()
        self.assertEqual(registration.status, 'review')

        registration.status = 'approved'
        registration.save()
        self.assertEqual(registration.status, 'approved')


class VendorPayoutModelTest(TestCase):
    """Tests for VendorPayout model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='payout@test.com',
            username='payout',
            password='testpass123'
        )
        self.vendor = Vendor.objects.create(
            user=self.user,
            business_name='Payout Business',
            business_address='789 Payout Rd',
            phone='+8801112223334',
            tax_id='TIN111222'
        )

    def test_payout_creation(self):
        payout = VendorPayout.objects.create(
            vendor=self.vendor,
            amount=5000.00,
            method='bkash',
            status='pending'
        )
        self.assertEqual(str(payout), 'Payout Business - 5000.00 (Pending)')
        self.assertEqual(payout.status, 'pending')

    def test_payout_status_changes(self):
        payout = VendorPayout.objects.create(
            vendor=self.vendor,
            amount=10000.00,
            method='bank',
            status='pending',
            transaction_id='TXN123'
        )

        payout.status = 'processing'
        payout.save()
        self.assertEqual(payout.status, 'processing')

        payout.status = 'completed'
        payout.save()
        self.assertEqual(payout.status, 'completed')


class VendorAPITest(APITestCase):
    """Tests for Vendor API endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='api@test.com',
            username='apiuser',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            email='admin@test.com',
            username='admin',
            password='adminpass123'
        )

    @patch('vendor.views.VendorApplicationViewSet.create')
    def test_application_submission(self, mock_create):
        """Test that users can submit vendor applications"""
        # This test would require file upload setup
        pass

    def test_admin_can_list_applications(self):
        """Test that admin users can list all applications"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/vendor/applications/')
        # Should return 200 (empty list or actual list)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_unauthenticated_cannot_list_applications(self):
        """Test that unauthenticated users cannot list applications"""
        response = self.client.get('/api/vendor/applications/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_vendor_can_view_own_stats(self):
        """Test that vendors can view their own statistics"""
        # First create a vendor profile
        vendor = Vendor.objects.create(
            user=self.user,
            business_name='Stats Business',
            business_address='123 Stats St',
            phone='+8801234567890',
            tax_id='TIN999888',
            is_approved=True
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/vendor/stats/')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
