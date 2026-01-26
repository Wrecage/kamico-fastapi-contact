import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def generate_report():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)

    # Get current month start
    first_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0).isoformat()

    print(f"\n--- 📊 Kamico Usage Report ({datetime.now().strftime('%B %Y')}) ---")
    
    # Fetch all clients
    clients = supabase.table("clients").select("id, client_name").execute().data

    for client in clients:
        # Count logs for this client since the start of the month
        logs = supabase.table("email_logs") \
            .select("id", count="exact") \
            .eq("client_id", client["id"]) \
            .gte("sent_at", first_of_month) \
            .execute()
        
        count = logs.count if logs.count is not None else 0
        status = "🟢 Active" if count > 0 else "⚪ Idle"
        
        print(f"{status} | {client['client_name']:<20} | Emails Sent: {count}")

if __name__ == "__main__":
    generate_report()