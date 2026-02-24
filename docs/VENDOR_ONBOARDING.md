# Vendor Onboarding System

## Overview

The Vendor Onboarding System allows businesses to register as vendors on the Fabrything e-commerce platform. The system includes a 4-step application process, admin approval workflow, and a vendor dashboard.

## Registration Flow

```
1. User visits /become-vendor
2. User fills out 4-step form:
   - Step 1: Business Information
   - Step 2: Document Upload (NID, Trade License, TIN)
   - Step 3: Payout Details (bKash/Nagad/Bank)
   - Step 4: Review & Submit
3. Application submitted for admin review
4. Admin reviews and approves/rejects
5. Approved vendors can access dashboard
```

## Required Documents

| Business Type | Required Documents |
|--------------|-------------------|
| Individual   | NID (required), TIN (optional) |
| Partnership  | NID (required), Trade License (optional), TIN (optional) |
| Company      | NID (required), Trade License (required), TIN (optional) |
| Corporation  | NID (required), Trade License (required), TIN (required) |

## Approval Criteria

Applications are reviewed based on:
- Valid business registration documents
- Complete information provided
- Valid NID number
- Valid payout account
- Compliance with platform terms

## Commission Structure

- **Default Commission**: 10% per sale
- Commission is deducted from each transaction
- Vendors can view their commission rate in the dashboard

## Payout Schedule

- **Frequency**: Weekly (every Sunday)
- **Minimum Payout**: ৳500
- **Methods**:
  - bKash (Instant transfer)
  - Nagad (Instant transfer)
  - Bank Transfer (2-3 business days)

## Payout Methods (Bangladesh Market)

### bKash
- Instant transfers to bKash accounts
- Account must be verified
- Format: 01XXXXXXXXX

### Nagad
- Instant transfers to Nagad accounts
- Account must be verified
- Format: 01XXXXXXXXX

### Bank Transfer
- Available for all banks in Bangladesh
- Requires full bank account details
- Processing time: 2-3 business days

## Testing Instructions

### 1. Submit Application
```
POST /api/vendor/applications/
Content-Type: multipart/form-data

Fields:
- business_name: string
- business_type: individual|partnership|company|corporation
- business_address: text
- phone: string
- tax_id: string
- nid_document: file
- trade_license: file (optional)
- tin_certificate: file (optional)
- payout_method: bank|bkash|nagad
- payout_account: string
```

### 2. Check Application Status
```
GET /api/vendor/my-application/my_status/
Authorization: Bearer <token>
```

### 3. Admin Approval
```
POST /api/vendor/applications/{id}/approve/
Authorization: Bearer <admin_token>

Body: { "notes": "Approval notes" }
```

### 4. Access Dashboard
```
GET /api/vendor/stats/
Authorization: Bearer <vendor_token>
```

## Mobile-First Features

- Touch-friendly buttons (minimum 44px)
- Large form inputs for mobile keyboards
- File upload with camera access
- Responsive design starting from 320px width
- Prominent bKash/Nagad payment options
