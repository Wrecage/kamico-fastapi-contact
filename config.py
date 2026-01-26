import os
from typing import List
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration loaded from environment variables"""
    

    # Supabase Credentials
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") 

    # Initialize Supabase Client
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        supabase = None


    # Master Encryption (Optional but recommended)
    ENCRYPTION_KEY = os.getenv("MASTER_ENCRYPTION_KEY")

    # Generate this using: Fernet.generate_key().decode()
    cipher = Fernet(ENCRYPTION_KEY.encode()) if ENCRYPTION_KEY else None

    @staticmethod
    def decrypt_password(encrypted_password: str) -> str:
        if not Config.cipher: return encrypted_password
        return Config.cipher.decrypt(encrypted_password.encode()).decode()

    # --- Static Fallbacks (Keep for your own portfolio use) ---
    ALLOWED_ORIGINS: List[str] = [
        o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()
    ]
    MAX_REQUESTS_PER_HOUR: int = int(os.getenv("MAX_REQUESTS_PER_HOUR", 10))



    # SMTP Configuration
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD: str = os.getenv("SENDER_PASSWORD")
    RECIPIENT_EMAIL: str = os.getenv("RECIPIENT_EMAIL")
    

    # API Security
    API_KEY: str = os.getenv("API_KEY")

    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv("ALLOWED_ORIGINS").split(",")
        if origin.strip()
    ]
    
    # Rate Limiting
    MAX_REQUESTS_PER_HOUR: int = int(os.getenv("MAX_REQUESTS_PER_HOUR"))
    
    # Security
    HONEYPOT_FIELD: str = "honeypot"
    
    # Validation Limits
    FIRST_NAME_MIN_LENGTH: int = 2
    FIRST_NAME_MAX_LENGTH: int = 50
    LAST_NAME_MIN_LENGTH: int = 2
    LAST_NAME_MAX_LENGTH: int = 50
    SUBJECT_MIN_LENGTH: int = 3
    SUBJECT_MAX_LENGTH: int = 200   
    MESSAGE_MIN_LENGTH: int = 10
    MESSAGE_MAX_LENGTH: int = 5000

    # Address/Phone Limits
    PHONE_MIN_LENGTH: int = 7
    PHONE_MAX_LENGTH: int = 20
    ZIP_MIN_LENGTH: int = 2
    ZIP_MAX_LENGTH: int = 10
    
    # Spam Detection
    SPAM_KEYWORDS: List[str] = [
            'viagra', 'cialis', 'crypto', 'bitcoin', 
            'lottery', 'winner', 'casino', 'pills',
            'investment', 'free money', 'work from home'
    ]
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present"""
        errors = []
        
        required_vars = {
                "SENDER_EMAIL": cls.SENDER_EMAIL,
                "SENDER_PASSWORD": cls.SENDER_PASSWORD,
                "RECIPIENT_EMAIL": cls.RECIPIENT_EMAIL,
                "SMTP_SERVER": cls.SMTP_SERVER
            }

        for var_name, value in required_vars.items():
                if not value:
                    errors.append(f"{var_name} is not set")
            
        if errors:
                error_msg = "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
                raise ValueError(error_msg)
    
    @classmethod
    def display_config(cls) -> None:
            """Display current configuration (for debugging)"""
            print("=" * 50)
            print("📧 Kamico Contact Form API Configuration")
            print("=" * 50)
            print(f"SMTP Server     : {cls.SMTP_SERVER}:{cls.SMTP_PORT}")
            print(f"Sender Email    : {cls.SENDER_EMAIL}")
            print(f"Recipient Email : {cls.RECIPIENT_EMAIL}")
            print(f"Password Set    : {'✅' if cls.SENDER_PASSWORD else '❌'}")
            print(f"🔐 API Key Set  : {'✅ Yes' if cls.API_KEY else '⚠️  No (Insecure)'}")
            print(f"Connected to Supabase: {'✅' if cls.supabase else '❌'}")
            print(f"Encryption Active: {'✅' if cls.cipher else '❌'}")
            print(f"CORS Allowed    : {', '.join(cls.ALLOWED_ORIGINS)}")
            print(f"Rate Limit      : {cls.MAX_REQUESTS_PER_HOUR} req/hr")
            print(f"Validation      : Name({cls.FIRST_NAME_MIN_LENGTH}-{cls.FIRST_NAME_MAX_LENGTH}), "
                f"Msg({cls.MESSAGE_MIN_LENGTH}-{cls.MESSAGE_MAX_LENGTH})")
            print("=" * 50)
            print(f"Validation      : Name({cls.LAST_NAME_MIN_LENGTH}-{cls.LAST_NAME_MAX_LENGTH}), "
                f"Msg({cls.MESSAGE_MIN_LENGTH}-{cls.MESSAGE_MAX_LENGTH})")
            print("=" * 50)


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"\n⚠️  {e}\n")
    print("Please set the required environment variables in your .env file")
    print("See .env.example for reference\n")