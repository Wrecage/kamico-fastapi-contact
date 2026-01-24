# 📧 Kamico Contact Form API

---

## 🚀 Quick Start (Local Development)

### 1. Setup

```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# (See "Getting Gmail App Password" below)
```

### 2. Run API

```bash
uvicorn main:app --reload
```

Access at `http://localhost:8000`
- Test page: `http://localhost:8000/test`
- Health check: `http://localhost:8000/health`
- API: `http://localhost:8000/api/contact`


## 📋 API Endpoints

### `POST /api/contact`
Submit contact form

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Hello",
  "message": "This is a test message",
  "honeypot": ""
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Your message has been sent successfully!"
}
```

**Response (Error):**
```json
{
  "detail": "Too many requests. Please try again later."
}
```

### `GET /`
Health check

**Response:**
```json
{
  "status": "online",
  "service": "Portfolio Contact Form API"
}
```

## 🐛 Troubleshooting

**Email not sending?**
- Check Gmail App Password is correct
- Verify 2FA is enabled on your Google account
- Check PythonAnywhere error logs in Web tab

**Getting CORS errors?**
- Make sure your portfolio domain is in `ALLOWED_ORIGINS`
- Include `http://` or `https://` in the domain

**Rate limited?**
- Wait 1 hour, or adjust `MAX_REQUESTS_PER_HOUR` in code



