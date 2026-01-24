

import os
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from contextlib import asynccontextmanager
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from collections import defaultdict
import re

# Import configuration
from config import Config

# ====================
# LIFESPAN EVENTS
# ====================
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Startup: Display configuration
    Config.display_config()
    yield
    # Shutdown: Cleanup if needed (currently none)
    print("\n👋 Shutting down Contact Form API...\n")

app = FastAPI(
    title="Kamico Contact Form API",
    lifespan=lifespan
)

# ====================
# SECURITY: API KEY VALIDATION
# ====================
def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> bool:
    """Verify API key from request header"""
    if not Config.API_KEY:
        # If no API key is set in config, allow request (backward compatibility)
        return True
    
    if x_api_key != Config.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return True

# ====================
# SECURITY: CORS
# ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],   
    allow_headers=["X-API-Key", "Content-Type", "Authorization"],
)

# ====================
# SECURITY: RATE LIMITING
# ====================
rate_limit_store = defaultdict(list)

def check_rate_limit(ip: str) -> bool:
    """Allow max requests per hour per IP based on config"""
    now = datetime.now()
    hour_ago = now - timedelta(hours=1)
    
    # Clean old entries
    rate_limit_store[ip] = [
        timestamp for timestamp in rate_limit_store[ip] 
        if timestamp > hour_ago
    ]
    
    # Check limit
    if len(rate_limit_store[ip]) >= Config.MAX_REQUESTS_PER_HOUR:
        return False
    
    rate_limit_store[ip].append(now)
    return True

class ContactForm(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    street: str
    city: str
    state: str
    zip_code: str
    subject: str
    message: str
    honeypot: Optional[str] = "" # for bot trapping
    
    
    @field_validator('first_name')
    @classmethod
    def validate_first_name(cls, v):
        v = v.strip()
        if len(v) < Config.FIRST_NAME_MIN_LENGTH or len(v) > Config.FIRST_NAME_MAX_LENGTH:
            raise ValueError(
                f'First name must be between {Config.FIRST_NAME_MIN_LENGTH} and {Config.FIRST_NAME_MAX_LENGTH} characters'
            )
        if not re.match(r"^[a-zA-Z\u00C0-\u017F\s\'-]+$", v):
            raise ValueError('Name contains invalid characters')
        return v
    
    @field_validator('last_name')
    @classmethod
    def validate_last_name(cls, v):
        v = v.strip()
        if len(v) < Config.LAST_NAME_MIN_LENGTH or len(v) > Config.LAST_NAME_MAX_LENGTH:
            raise ValueError(
                f'Last name must be between {Config.LAST_NAME_MIN_LENGTH} and {Config.LAST_NAME_MAX_LENGTH} characters'
            )
        if not re.match(r"^[a-zA-Z\u00C0-\u017F\s\'-]+$", v):
            raise ValueError('Name contains invalid characters')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        # Basic regex for phone: allows +, digits, spaces, and dashes
        if not re.match(r'^\+?[\d\s\-]{7,20}$', v):
            raise ValueError('Invalid phone number format')
        return v
    


    @field_validator('street')
    @classmethod
    def validate_street(cls, v):
        v = v.strip()
        if len(v) < 5:
            raise ValueError('Street address is too short')
        return v

    @field_validator('city')
    @classmethod
    def validate_city(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError('City name is too short')
        return v

    @field_validator('state')
    @classmethod
    def validate_state(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError('Please provide a valid State/Province')
        return v

    @field_validator('zip_code')
    @classmethod
    def validate_zip(cls, v):
        v = v.strip()
        # Using the lengths from your Config class
        if len(v) < Config.ZIP_MIN_LENGTH or len(v) > Config.ZIP_MAX_LENGTH:
            raise ValueError(f'Zip code must be between {Config.ZIP_MIN_LENGTH} and {Config.ZIP_MAX_LENGTH} characters')
        # Check if it's alphanumeric (handles US 12345 and UK/Canada A1B 2C3)
        if not re.match(r"^[a-zA-Z0-9\s-]+$", v):
            raise ValueError('Invalid Zip/Postal code format')
        return v
    
    
    @field_validator('subject')
    @classmethod
    def validate_subject(cls, v):
        v = v.strip()
        if len(v) < Config.SUBJECT_MIN_LENGTH or len(v) > Config.SUBJECT_MAX_LENGTH:
            raise ValueError(f'Subject must be between {Config.SUBJECT_MIN_LENGTH} and {Config.SUBJECT_MAX_LENGTH} characters')
        return v
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        v = v.strip()
        if len(v) < Config.MESSAGE_MIN_LENGTH or len(v) > Config.MESSAGE_MAX_LENGTH:
            raise ValueError(f'Message must be between {Config.MESSAGE_MIN_LENGTH} and {Config.MESSAGE_MAX_LENGTH} characters')
        if any(keyword in v.lower() for keyword in Config.SPAM_KEYWORDS):
            raise ValueError('Message contains spam content')
        return v

# ====================
# EMAIL SENDING
# ====================
def send_email(form_data: ContactForm) -> bool:
    """Send email via SMTP using configuration"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"New Inquiry: {form_data.subject}"
        msg["From"] = Config.SENDER_EMAIL
        msg["To"] = Config.RECIPIENT_EMAIL
        msg["Reply-To"] = form_data.email
        
        # Comprehensive Email body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px;">New Contact Submission</h2>
                    
                    <p><strong>Name:</strong> {form_data.first_name} {form_data.last_name}</p>
                    <p><strong>Email:</strong> {form_data.email}</p>
                    <p><strong>Phone:</strong> {form_data.phone}</p>
                    
                    <h3 style="color: #7f8c8d; font-size: 16px;">Address Details</h3>
                    <p style="background: #f9f9f9; padding: 10px; border-radius: 4px;">
                        {form_data.street}<br>
                        {form_data.city}, {form_data.state} {form_data.zip_code}
                    </p>
                    
                    <hr style="border: 0; border-top: 1px solid #eee;">
                    <p><strong>Subject:</strong> {form_data.subject}</p>
                    <p><strong>Message:</strong></p>
                    <div style="white-space: pre-wrap; background: #fdfdfd; padding: 15px; border-left: 4px solid #3498db;">
                        {form_data.message}
                    </div>
                    
                    <p style="color: #999; font-size: 11px; margin-top: 30px; text-align: center;">
                        Received on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, "html"))
        
        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.starttls()
            server.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Email error: {str(e)}")
        return False
    

# ====================
# API ENDPOINTS
# ====================
@app.post("/api/contact")
async def contact_form(
    form: ContactForm, 
    request: Request
):
    """Handle contact form submission"""
    
    # Get client IP
    client_ip = request.headers.get("x-forwarded-for", request.client.host)   

    # SECURITY: Check honeypot (bot trap)
    if form.honeypot and form.honeypot.strip():
        raise HTTPException(status_code=400, detail="Invalid submission")
    
    # SECURITY: Rate limiting
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429, 
            detail="Too many requests. Please try again later."
        )
    
    # Send email
    success = send_email(form)
    
    if not success:
        raise HTTPException(
            status_code=500, 
            detail="Failed to send message. Please try again."
        )
    
    return {
        "success": True,
        "message": "Your message has been sent successfully!"
    }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Portfolio Contact Form API",
        "version": "1.0.0",
        "endpoints": {
            "contact": "/api/contact (POST)",
            "health": "/ (GET)"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "smtp_configured": bool(Config.SENDER_EMAIL and Config.SENDER_PASSWORD),
        "allowed_origins": len(Config.ALLOWED_ORIGINS)
    }

@app.get("/test")
async def get_test_page():
    path = os.path.join(os.path.dirname(__file__), "test.html")
    return FileResponse("test.html")

# At the end of main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)