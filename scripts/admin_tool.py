import os
import secrets
import string
from cryptography.fernet import Fernet
from supabase import create_client, Client
from dotenv import load_dotenv

# Load your production/local .env
load_dotenv()

class KamicoAdmin:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        master_key = os.getenv("MASTER_ENCRYPTION_KEY")

        if not all([url, key, master_key]):
            raise ValueError("Missing SUPABASE_URL, SERVICE_ROLE_KEY, or MASTER_ENCRYPTION_KEY in .env")

        self.supabase: Client = create_client(url, key)
        self.cipher = Fernet(master_key.encode())

    def generate_api_key(self, length=32):
        """Generates a secure, random API Key"""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def encrypt_password(self, raw_password: str):
        """Encrypts the SMTP App Password"""
        return self.cipher.encrypt(raw_password.encode()).decode()

    def add_client(self):
        print("\n--- 🆕 Register New Client to Kamico API ---")
        client_name = input("Client Name: ")
        sender_email = input("Sender Email (SMTP User): ")
        raw_password = input("Sender App Password: ")
        recipient_email = input("Recipient Email (Where leads go): ")
        origins = input("Allowed Origins (comma-separated, e.g. https://site.com): ").split(",")
        
        # Clean origins
        allowed_origins = [o.strip() for o in origins if o.strip()]
        
        # Security Processing
        api_key = self.generate_api_key()
        encrypted_pass = self.encrypt_password(raw_password)

        # Prepare Data
        client_data = {
            "client_name": client_name,
            "api_key": api_key,
            "sender_email": sender_email,
            "sender_password": encrypted_pass,
            "recipient_email": recipient_email,
            "allowed_origins": allowed_origins,
            "smtp_server": "smtp.gmail.com", # Default
            "smtp_port": 587
        }

        # Push to Supabase
        try:
            result = self.supabase.table("clients").insert(client_data).execute()
            print("\n✅ Success! Client Registered.")
            print(f"🚀 API KEY: {api_key}")
            print(f"⚠️  Give this key to the client. It will not be shown again in plain text.")
        except Exception as e:
            print(f"\n❌ Failed to add client: {e}")

if __name__ == "__main__":
    admin = KamicoAdmin()
    admin.add_client()