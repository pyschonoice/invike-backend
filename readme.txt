# Invike Backend

A modular Django REST Framework backend for the Invike event management platform.

## Overview

Invike is a modern event invitation and RSVP platform with the following key features:

- User authentication (Google, Apple, Email)
- Event creation and management
- RSVP system with approval options
- Manual payment confirmation
- Notifications for event updates

## Project Structure

The backend is organized into modular apps for better maintainability:

- **Users**: Authentication and user management
- **Events**: Event creation and management
- **RSVP**: RSVP management and guest lists
- **Payments**: Payment links and confirmation
- **Notifications**: System notifications and alerts
- **Core**: Shared functionality across modules

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL (recommended) or SQLite

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/invike-backend.git
   cd invike-backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your database in `config/settings.py` (default is SQLite)

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

The server will be available at http://localhost:8000/

## API Testing without Frontend

You can test the API without a frontend using the following methods:

### 1. Django Admin

Access the admin panel at http://localhost:8000/admin/ to manage data directly. This is useful for:
- Creating users
- Managing events
- Reviewing RSVPs
- Checking payment status
- Setting up test data

### 2. API Documentation

Browse the auto-generated API documentation at http://localhost:8000/api/docs/ to understand the available endpoints and their parameters.

### 3. Postman Collection

A Postman collection is included in the `postman` directory. To use it:

1. Import the collection into Postman
2. Set up an environment with the following variables:
   - `base_url`: http://localhost:8000
   - `token`: (will be filled after login)
   - `event_id`: (will be filled after creating an event)
   - `user_id`: (will be filled after registration)

3. Execute the requests in the following order:
   - Register a new user
   - Login to get the JWT token (will be automatically saved to the `token` variable)
   - Create an event (will save the event ID to the `event_id` variable)
   - Test RSVP, payments, and notifications endpoints

### 4. Curl Commands

You can also test the API with curl commands. Here are some examples:

**Register a new user:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "testpass123", "role": "HOST"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'
```

**Create an event (replace TOKEN with your JWT token):**
```bash
curl -X POST http://localhost:8000/api/events/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"title": "Test Event", "description": "This is a test event", "date": "2023-12-31T19:00:00Z", "location": "Test Venue", "privacy": "PUBLIC"}'
```

## Module Testing

Each module includes its own test suite. To run tests for a specific module:

```bash
python manage.py test apps.users
python manage.py test apps.events
python manage.py test apps.rsvp
python manage.py test apps.payments
python manage.py test apps.notifications
```

To run all tests:

```bash
python manage.py test
```

## API Endpoints Overview

### Authentication

- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login and get JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/update/` - Update user profile

### Events

- `GET /api/events/` - List all visible events
- `POST /api/events/` - Create a new event
- `GET /api/events/{id}/` - Get event details
- `PUT/PATCH /api/events/{id}/` - Update event
- `DELETE /api/events/{id}/` - Delete event
- `GET /api/events/{id}/share/` - Get event sharing options

### RSVP

- `POST /api/rsvp/` - Create a new RSVP
- `GET /api/rsvp/` - List user's RSVPs
- `PUT/PATCH /api/rsvp/{id}/` - Update RSVP
- `GET /api/rsvp/events/{event_id}/guests/` - Get event guest list
- `GET /api/rsvp/events/{event_id}/guests/export/` - Export guest list as CSV

### Payments

- `POST /api/payments/add-link/` - Add payment link (host)
- `POST /api/payments/confirm/` - Confirm payment (guest)
- `GET /api/payments/event-status/` - Check event payment status
- `PATCH /api/payments/{id}/update-status/` - Update payment status (host)

### Notifications

- `GET /api/notifications/` - List user's notifications
- `POST /api/notifications/` - Create notification (host)
- `POST /api/notifications/mark-read/` - Mark notifications as read
- `POST /api/notifications/mark-all-read/` - Mark all notifications as read
- `GET /api/notifications/unread-count/` - Get unread notification count

## Development and Extension

### Adding New Modules

To add a new module:

1. Create a new app in the `apps` directory:
   ```bash
   python manage.py startapp new_module apps/new_module
   ```

2. Add the module to `INSTALLED_APPS` in `config/settings.py`:
   ```python
   INSTALLED_APPS = [
       # ...
       'apps.new_module',
   ]
   ```

3. Create models, serializers, views, and URLs following the existing pattern

4. Include your module's URLs in `config/urls.py`:
   ```python
   urlpatterns = [
       # ...
       path('api/new-module/', include('apps.new_module.urls')),
   ]
   ```

### Webhooks for Future Integrations

The backend includes placeholder endpoints for webhooks that can be used for future integrations:

- `/api/webhooks/payment-success/` - For successful payment integrations
- `/api/webhooks/payment-failed/` - For failed payment notifications
- `/api/webhooks/rsvp-update/` - For external RSVP updates

## Deployment

For production deployment:

1. Set `DEBUG = False` in settings
2. Use a proper production database (PostgreSQL recommended)
3. Set up environment variables for sensitive information
4. Configure proper CORS settings
5. Use a production WSGI server like Gunicorn
6. Set up a reverse proxy like Nginx

Example deployment command:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## License

[MIT License](LICENSE.md)