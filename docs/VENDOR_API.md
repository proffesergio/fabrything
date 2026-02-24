# Vendor API Documentation

## Base URL
```
http://localhost:8000/api/vendor/
```

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Endpoints

### 1. Submit Vendor Application
**Public Endpoint** - No authentication required (optional)

```
POST /api/vendor/applications/
Content-Type: multipart/form-data
```

**Request Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| business_name | string | Yes | Business name |
| business_type | string | Yes | individual, partnership, company, corporation |
| business_address | text | Yes | Complete business address |
| phone | string | Yes | Contact phone number |
| tax_id | string | Yes | Tax Identification Number |
| nid_document | file | Yes | NID image/PDF |
| trade_license | file | No | Trade license document |
| tin_certificate | file | No | TIN certificate |
| payout_method | string | Yes | bank, bkash, nagad |
| payout_account | string | Yes | Account number or mobile number |

**Response (201 Created):**
```json
{
  "message": "Application submitted successfully",
  "data": {
    "id": 1,
    "business_name": "My Shop",
    "business_type": "company",
    "status": "pending",
    "created_at": "2026-02-20T10:00:00Z"
  }
}
```

### 2. List All Applications (Admin Only)

```
GET /api/vendor/applications/
Authorization: Bearer <admin_token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| search | string | Search by business name, email, phone |
| ordering | string | Order by: created_at, status, business_name |
| status | string | Filter by status: pending, review, approved, rejected |

**Response (200 OK):**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "user_email": "vendor@example.com",
      "user_name": "John Doe",
      "business_name": "My Shop",
      "business_type": "company",
      "phone": "+8801234567890",
      "status": "pending",
      "created_at": "2026-02-20T10:00:00Z"
    }
  ]
}
```

### 3. Get Application Details (Admin Only)

```
GET /api/vendor/applications/{id}/
Authorization: Bearer <admin_token>
```

### 4. Approve Application (Admin Only)

```
POST /api/vendor/applications/{id}/approve/
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "notes": "All documents verified. Approved."
}
```

**Response:**
```json
{
  "message": "Application approved successfully"
}
```

### 5. Reject Application (Admin Only)

```
POST /api/vendor/applications/{id}/reject/
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "notes": "Incomplete documents. Please resubmit."
}
```

### 6. Mark as Under Review (Admin Only)

```
POST /api/vendor/applications/{id}/mark_review/
Authorization: Bearer <admin_token>
```

### 7. Get Current User's Application Status

```
GET /api/vendor/my-application/my_status/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "business_name": "My Shop",
  "status": "pending",
  "admin_notes": "",
  "created_at": "2026-02-20T10:00:00Z",
  "updated_at": "2026-02-20T10:00:00Z"
}
```

### 8. Get Vendor Profile

```
GET /api/vendor/profile/me/
Authorization: Bearer <vendor_token>
```

**Response:**
```json
{
  "id": 1,
  "user_email": "vendor@example.com",
  "user_name": "John Doe",
  "business_name": "My Shop",
  "business_address": "123 Main St, Dhaka",
  "phone": "+8801234567890",
  "tax_id": "TIN123456",
  "is_approved": true,
  "approved_at": "2026-02-20T12:00:00Z",
  "commission_rate": "10.00",
  "total_sales": "50000.00",
  "pending_payout": "5000.00",
  "created_at": "2026-02-20T10:00:00Z"
}
```

### 9. Update Vendor Profile

```
PATCH /api/vendor/profile/me/
Authorization: Bearer <vendor_token>
```

**Request Body:**
```json
{
  "business_address": "New Address",
  "phone": "+8809876543210"
}
```

### 10. Get Vendor Dashboard Stats

```
GET /api/vendor/stats/
Authorization: Bearer <vendor_token>
```

**Response:**
```json
{
  "business_name": "My Shop",
  "total_sales": 50000.00,
  "pending_payout": 5000.00,
  "commission_rate": 10.00,
  "total_orders": 45,
  "total_products": 20,
  "is_approved": true,
  "recent_payouts": [],
  "sales_by_month": [],
  "recent_orders": []
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error |

## Example: Complete Application Flow

```javascript
// 1. Submit application
const formData = new FormData();
formData.append('business_name', 'My Shop');
formData.append('business_type', 'company');
formData.append('business_address', '123 Main St, Dhaka');
formData.append('phone', '+8801234567890');
formData.append('tax_id', 'TIN123456');
formData.append('nid_document', nidFile);
formData.append('payout_method', 'bkash');
formData.append('payout_account', '01712345678');

await fetch('/api/vendor/applications/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  },
  body: formData
});

// 2. Check status
const status = await fetch('/api/vendor/my-application/my_status/', {
  headers: { 'Authorization': 'Bearer ' + token }
});

// 3. View dashboard (after approval)
const stats = await fetch('/api/vendor/stats/', {
  headers: { 'Authorization': 'Bearer ' + token }
});
```
