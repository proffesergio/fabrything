# Fabrything - AI-Powered E-Commerce Platform

Modern e-commerce platform for clothing, built with Django and React.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip
- virtualenv

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/fabrything.git
cd fabrything

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## 📚 API Documentation

### Swagger UI
Visit: `http://localhost:8000/api/docs/`

### ReDoc
Visit: `http://localhost:8000/api/redoc/`

### API Endpoints

**Authentication**
- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/refresh/` - Refresh token
- `GET /api/v1/auth/me/` - Get current user

**Products**
- `GET /api/v1/products/` - List products
- `GET /api/v1/products/{pid}/` - Get product details
- `GET /api/v1/products/featured/` - Get featured products
- `GET /api/v1/products/{pid}/related/` - Get related products

**Reviews**
- `GET /api/v1/reviews/` - List reviews
- `POST /api/v1/reviews/` - Create review
- `PUT /api/v1/reviews/{id}/` - Update review
- `DELETE /api/v1/reviews/{id}/` - Delete review

**Cart**
- `GET /api/v1/cart/current_cart/` - Get current cart
- `POST /api/v1/cart/add_item/` - Add to cart
- `POST /api/v1/cart/remove_item/` - Remove from cart

**Wishlist**
- `GET /api/v1/wishlist/` - Get wishlist
- `POST /api/v1/wishlist/add/` - Add to wishlist
- `POST /api/v1/wishlist/remove/` - Remove from wishlist

**Addresses**
- `GET /api/v1/addresses/` - Get addresses
- `POST /api/v1/addresses/` - Create address
- `PUT /api/v1/addresses/{id}/` - Update address
- `DELETE /api/v1/addresses/{id}/` - Delete address

## 🔐 Environment Variables

See `.env.example` for all available configuration options.

**Important**: Never commit `.env` to git repository!

## 📝 Git Workflow

```bash
# Create feature branch
git checkout -b feature/api-setup

# Make changes and commit
git add .
git commit -m "feat: implement DRF API with JWT authentication"

# Push to GitHub
git push origin feature/api-setup

# Create Pull Request on GitHub
```

## 📦 Project Structure

```
fabrything/
├── fabrythingapp/
│   ├── migrations/
│   ├── services/
│   │   ├── product_service.py
│   │   ├── review_service.py
│   │   └── cart_service.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── api_urls.py
│   └── tests.py
├── userauthapp/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── api_urls.py
├── shared_utils/
│   ├── exceptions.py
│   ├── pagination.py
│   └── permissions.py
├── shopfabrything/
│   └── settings.py
├── templates/
├── static/
├── media/
├── logs/
├── .env.example
├── requirements.txt
└── manage.py
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test fabrythingapp

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 🐳 Docker (Coming Soon)

Docker configuration for microservices will be added in Phase 3.

## 📄 License

MIT License - See LICENSE file for details

## 👥 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📧 Support

For support, email support@fabrything.com

## 🎯 Roadmap

- [ ] **Phase 1** ✅ API Layer & Foundation
  - ✅ DRF Setup
  - ✅ JWT Authentication
  - ✅ Swagger Documentation
  - ✅ Service Layer

- [ ] **Phase 2** - Advanced Features
  - [ ] AI Product Recommendations
  - [ ] AR Virtual Try-On
  - [ ] Advanced Search with Filters
  - [ ] Payment Integration

- [ ] **Phase 3** - Microservices Migration
  - [ ] Modular Monolith
  - [ ] Service Extraction
  - [ ] Docker & Kubernetes
  - [ ] API Gateway

- [ ] **Phase 4** - Frontend Modernization
  - [ ] Next.js 14 Migration
  - [ ] React Components
  - [ ] Framer Motion Animations
  - [ ] TailwindCSS Styling

---

**Last Updated:** January 28, 2026
**Status:** Active Development

📚 Swagger UI: http://localhost:8000/api/docs/
📚 ReDoc: http://localhost:8000/api/redoc/
📄 Schema: http://localhost:8000/api/schema/

👤 Register: POST /api/v1/auth/register/
🔑 Login: POST /api/v1/auth/login/
📦 Products: GET /api/v1/products/
⭐ Reviews: GET /api/v1/reviews/
🛒 Cart: GET /api/v1/cart/current_cart/
❤️ Wishlist: GET /api/v1/wishlist/