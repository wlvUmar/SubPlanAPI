# FastAPI Subscription Microservice

A FastAPI-based subscription management system with JWT authentication, email verification, and password management.

## Features

- **User Authentication**: Register, login, logout, and JWT token management
- **Email Verification**: Email-based account verification
- **Password Management**: Forgot password, reset password, and change password
- **Session Management**: Logout single device or all devices
- **Token Refresh**: Secure token rotation system
- **User Profile**: Get current user information
- **Admin Panel**: With simple CRUD features



## Tech Stack

- **FastAPI** - Modern web framework
- **SQLAlchemy** (async) - Database ORM
- **PostgreSQL** (asyncpg) - Database
- **PyJWT** - JWT token handling
- **passlib + bcrypt** - Password hashing
- **email-validator** - Email validation
- **colorlog** - Colored logging


## 📘 API Docs (Swagger UI)
![Swagger UI](./images/docs.png)

## 🔐 Admin Panel Login
![Admin Login](./images/adminlogin.png)

## 🧭 Admin Panel Dashboard
![Admin Dashboard](./images/adminka.png)

## API Endpoints

### Authentication

- `POST /user/register` - Register a new user
- `POST /user/login` - Login and receive tokens
- `POST /user/refresh` - Refresh access token using refresh token
- `POST /user/logout` - Logout current device
- `POST /user/logout-all` - Logout all devices

### User Management

- `GET /user/me` - Get current user information
- `PUT /user/change-password` - Change password (requires authentication)

### Email Verification

- `GET /user/verify?token=...` - Verify email address

### Password Reset

- `POST /user/forgot-password?email=...` - Request password reset email
- `GET /user/reset-password?token=...` - Password reset form
- `POST /user/reset-password` - Submit password reset

### Subscription Plans (Admin only for create/update/delete)

- `GET /plans/` - Get all available plans
- `GET /plans/{plan_name}` - Get specific plan details
- `POST /plans/` - Create new plan (admin only)
- `PUT /plans/{plan_name}` - Update plan (admin only)
- `DELETE /plans/{plan_name}` - Delete plan (admin only)

### Subscriptions

- `GET /subscriptions/me` - Get user's subscriptions
- `POST /subscriptions/` - Create new subscription
- `GET /subscriptions/{subscription_id}` - Get subscription details
- `PATCH /subscriptions/{subscription_id}/cancel` - Cancel subscription
- `GET /subscriptions/` - Get all subscriptions (admin only)

### Payments

- `GET /payments/me` - Get user's payment history
- `POST /payments/` - Create new payment
- `GET /payments/{payment_id}` - Get payment details
- `PATCH /payments/{payment_id}` - Update payment status
- `GET /payments/` - Get all payments (admin only)

### Invoices & Discounts

- `GET /invoices/me` - Get user's invoices
- `GET /invoices/{invoice_id}` - Get invoice details
- `GET /invoices/` - Get all invoices (admin only)
- `GET /invoices/discounts` - Get all discount codes
- `POST /invoices/discounts` - Create discount code (admin only)
- `DELETE /invoices/discounts/{discount_id}` - Delete discount code (admin only)

## Database Models

- **User** - User accounts with authentication
- **Subscription** - User subscriptions
- **Plan** - Subscription plans (basic, business, enterprise)
- **Payment** - Payment records
- **Invoice** - Invoice records
- **Discount** - Discount codes
- **RefreshToken** - JWT refresh tokens

## Configuration

Update settings in `config.py`:
- Database URL
- JWT secret key
- Email configuration
- Algorithm settings

## Logging

Logs are written to both console (colored) and `app.log` file with rotation support.

