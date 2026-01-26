

import os
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Dict
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
    allow_origins=["*"],
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
def send_email(form_data: ContactForm, client: Dict) -> bool:
    """Send email via SMTP using configuration"""
    try:

        # Decrypt the App Password from Supabase
        real_password = Config.decrypt_password(client['sender_password'])

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[{client['client_name']}] New Inquiry: {form_data.subject}"
        msg["From"] = client['sender_email']
        msg["To"] = client['recipient_email']
        msg["Reply-To"] = form_data.email
        
        # Comprehensive Email body
        html_body = f"""
        <html>
        <body style="font-family: 'JetBrains Mono', 'Courier New', monospace; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 3px solid #341409;">
                <!-- Header -->
                <div style="background-color: #333333; padding: 28px 25px; border-bottom: 3px solid #FFC0CB;">
                    <h1 style="margin: 0; color: #ccc2ab; font-size: 20px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;">New Contact Submission</h1>
                </div>

                <!-- Contact Info -->
                <div style="padding: 28px 25px;">
                    <div style="margin-bottom: 20px;">
                        <p style="margin: 0 0 4px 0; color: #341409; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">Name</p>
                        <p style="margin: 0; color: #4f3736; font-size: 14px; line-height: 1.5;">{form_data.first_name} {form_data.last_name}</p>
                    </div>

                    <div style="margin-bottom: 20px;">
                        <p style="margin: 0 0 4px 0; color: #333333; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">Email</p>
                        <p style="margin: 0; color: #4f3736; font-size: 14px; line-height: 1.5; font-weight: 600;">{form_data.email}</p>
                    </div>

                    <div style="margin-bottom: 0;">
                        <p style="margin: 0 0 4px 0; color: #333333; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">Phone</p>
                        <p style="margin: 0; color: #4f3736; font-size: 14px; line-height: 1.5; font-weight: 600;" >{form_data.phone}</p>
                    </div>
                </div>

                <!-- Address Section -->
                <div style="padding: 0 25px 28px 25px; border-top: 2px solid #e8e8e8;">
                    <p style="margin: 20px 0 12px 0; color: #333333; font-size: 10px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">Address</p>
                    <div style="border-left: 4px solid #FFC0CB; padding-left: 16px; background-color: #fafafa; padding: 14px 14px 14px 16px; border-left: 4px solid #FFC0CB;">
                        <p style="margin: 0; color: #4f3736; font-size: 13px; line-height: 1.6;">
                            {form_data.street}<br>
                            {form_data.city}, {form_data.state} {form_data.zip_code}
                        </p>
                    </div>
                </div>

                <!-- Subject Section -->
                <div style="padding: 0 25px 28px 25px; border-top: 2px solid #e8e8e8;">
                    <p style="margin: 20px 0 4px 0; color: #333333; font-size: 10px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">Subject</p>
                    <p style="margin: 0; color: #333333; font-size: 15px; line-height: 1.5; font-weight: 700;">{form_data.subject}</p>
                </div>

                <!-- Message Section -->
                <div style="padding: 0 25px 28px 25px; border-top: 2px solid #e8e8e8;">
                    <p style="margin: 20px 0 12px 0; color: #333333; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">Message</p>
                    <div style="background-color: #fafafa; padding: 16px; border-left: 4px solid #68809c; white-space: pre-wrap; border-left: 4px solid #68809c;">
                        <p style="margin: 0; color: #4f3736; font-size: 13px; line-height: 1.6; white-space: pre-wrap;">
                            {form_data.message}
                        </p>
                    </div>
                </div>

                <!-- Footer -->
                <div style="padding: 20px 25px; background-color: #333333; text-align: center; border-top: 3px solid #FFC0CB;">
                    <p style="margin: 0; color: #ccc2ab; font-size: 10px; letter-spacing: 0.5px;">
                        Submitted {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_body, "html"))
        
        with smtplib.SMTP(client['smtp_server'], client['smtp_port']) as server:
            server.starttls()
            server.login(client['sender_email'], real_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email error for {client['client_name']}: {str(e)}")
        return False
    

# ====================
# API ENDPOINTS
# ====================
@app.post("/api/contact")


async def contact_form(
    form: ContactForm, 
    request: Request,
    x_api_key: str = Header(None, alias="X-API-Key")
):
    

    # 1. API Key Check
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header required")
    
    # 2. Supabase Lookup
    try:
        res = Config.supabase.table("clients").select("*").eq("api_key", x_api_key).single().execute()
        client = res.data
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    

    # 3. Domain Validation (The real CORS)
    origin = request.headers.get("origin")
    # 1. Block anyone not using a browser (optional but safer)
    if not origin:
        raise HTTPException(status_code=403, detail="Direct API access not allowed")

    # 2. Match against the specific client's allowed list
    if origin not in client['allowed_origins']:
        # Log this attempt so you can see who is trying to use your API
        print(f"SECURITY ALERT: Unauthorized origin {origin} tried to use key for {client['client_name']}")
        raise HTTPException(status_code=403, detail="This domain is not authorized to use this API Key")



    """Handle contact form submission"""
    
    # Get client IP
    client_ip = request.headers.get("x-forwarded-for", request.client.host)   

    # SECURITY: Check honeypot (bot trap)
    if form.honeypot and form.honeypot.strip():
        raise HTTPException(status_code=400, detail="Invalid submission")
    
    # SECURITY: Rate limiting
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    # Send email
    success = send_email(form, client)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send message. Please try again.")
    
    # logging
    try:
        Config.supabase.table("email_logs").insert({
            "client_id": client["id"],
            "subject": form.subject,
            "sender_email": form.email
        }).execute()
    except Exception as e:
        print(f"Logging Error: {str(e)}")
    
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
    # This finds test.html in your root folder correctly on Vercel
    path = os.path.join(os.path.dirname(__file__), "..", "test.html") 
    # Note: the ".." is needed because index.py is inside /api/
    if not os.path.exists(path):
        # Fallback if you didn't use the api/ folder structure
        path = os.path.join(os.path.dirname(__file__), "test.html")
    return FileResponse(path)

# At the end of main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)