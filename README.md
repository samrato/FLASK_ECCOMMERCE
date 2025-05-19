# 🛒 Flask E-commerce API

A full-featured RESTful E-commerce API built with Flask, SQLAlchemy, JWT authentication, Cloudinary image uploads, Stripe payments, and more.

---
![Demo Image](images/demo.png)


## 🚀 Features

- ✅ User Authentication (JWT)
- 🛍️ Product, Category, Cart, Order, Payment Management
- 🖼️ Image Uploads via Cloudinary
- 💳 Stripe Payment Integration
- 📧 Email Notifications via Flask-Mail
- 🧾 Marshmallow Serialization
- 🔐 Role-based Access (Admin/User)
- 🌐 Clean modular structure
- 🔄 GitHub Actions CI/CD Workflow

---

## 🧠 Tech Stack

- Python 3.10
- Flask
- SQLAlchemy + Flask-Migrate
- Marshmallow
- Flask-JWT-Extended
- Flask-Mail
- Cloudinary
- Stripe
- SQLite / PostgreSQL
- GitHub Actions (CI)

---

SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
DATABASE_URL=sqlite:///ecommerce.db

MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_password
MAIL_DEFAULT_SENDER=your_email@example.com

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

