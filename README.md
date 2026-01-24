# 📧 Kamico Contact Form API

A production-ready FastAPI contact form service with email delivery, built-in security, and easy integration.

## ✨ Features

- ✅ **FastAPI** - Modern, fast Python framework
- ✅ **International Support** - Names with ñ, é, ü, etc.
- ✅ **Security** - CORS, rate limiting, bot protection, input validation
- ✅ **SQL Injection Safe** - No raw SQL queries
- ✅ **Email Delivery** - SMTP integration (Gmail compatible)
- ✅ **Error Handling** - Structured responses for easy frontend integration
- ✅ **Production Ready** - Tested, documented, deployable
- ✅ **Serverless** - Deploy on Vercel, PythonAnywhere, or any ASGI host

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

### 3. Deploy to Vercel (1 minute)

See [VERCEL_QUICK_START.md](./VERCEL_QUICK_START.md)
3. Search for **"App Passwords"**
4. Select app: **Mail**
5. Select device: **Other** (name it "Portfolio API")
6. Copy the 16-character password
7. Paste it in your `.env` file as `SENDER_PASSWORD`

### 3. Configure Environment Variables

Edit `.env` file:
```bash
SENDER_EMAIL=youremail@gmail.com
SENDER_PASSWORD=xxxx xxxx xxxx xxxx  # 16-char app password
RECIPIENT_EMAIL=youremail@gmail.com  # Where you receive messages
```

### 4. Update Allowed Domains

In `main.py`, update this section with YOUR portfolio domain(s):

```python
ALLOWED_ORIGINS = [
    "https://yourportfolio.com",
    "https://www.yourportfolio.com",
    "http://localhost:3000",  # For local testing
]
```

## 🌐 Deploy to PythonAnywhere (FREE Forever)

### Step 1: Create Account
- Go to https://pythonanywhere.com
- Sign up for **FREE Beginner Account**

### Step 2: Upload Files
1. Click **Files** tab
2. Create directory: `portfolio-contact-api`
3. Upload `main.py` and `requirements.txt`

### Step 3: Set Environment Variables
1. Click **Web** tab
2. Scroll to **Environment Variables**
3. Add:
   - `SENDER_EMAIL` → your-email@gmail.com
   - `SENDER_PASSWORD` → your-app-password
   - `RECIPIENT_EMAIL` → your-email@gmail.com

### Step 4: Configure Web App
1. Click **Web** tab → **Add a new web app**
2. Select **Manual configuration**
3. Select **Python 3.10**
4. In **WSGI configuration file**, replace content with:

```python
import sys
path = '/home/YOUR_USERNAME/portfolio-contact-api'
if path not in sys.path:
    sys.path.append(path)

from main import app as application
```

5. In **Virtualenv** section, enter:
   ```
   /home/YOUR_USERNAME/portfolio-contact-api/venv
   ```

### Step 5: Install Dependencies
1. Click **Consoles** tab → **Bash**
2. Run:
```bash
cd portfolio-contact-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 6: Reload & Test
1. Go to **Web** tab
2. Click **Reload** button
3. Visit: `https://YOUR_USERNAME.pythonanywhere.com`

### Step 7: Keep It Running Forever
- Every **3 months**, click the "Extend" button on PythonAnywhere
- That's it! 100% free forever.

## 🔒 Security Features

✅ **Rate Limiting** - Max 5 submissions/hour per IP  
✅ **CORS Protection** - Only your domains can access  
✅ **Honeypot Field** - Catches bots  
✅ **Input Validation** - Sanitizes all data  
✅ **Spam Detection** - Blocks common spam keywords  
✅ **Length Limits** - Prevents abuse  

## 💻 Frontend Integration

### HTML Form Example

```html
<form id="contactForm">
  <input type="text" name="name" placeholder="Your Name" required>
  <input type="email" name="email" placeholder="Your Email" required>
  <input type="text" name="subject" placeholder="Subject" required>
  <textarea name="message" placeholder="Your Message" required></textarea>
  
  <!-- Honeypot - hidden from users, catches bots -->
  <input type="text" name="honeypot" style="display:none" tabindex="-1" autocomplete="off">
  
  <button type="submit">Send Message</button>
</form>

<div id="status"></div>

<script>
document.getElementById('contactForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const form = e.target;
  const status = document.getElementById('status');
  const formData = new FormData(form);
  const data = Object.fromEntries(formData);
  
  status.textContent = 'Sending...';
  
  try {
    const response = await fetch('https://YOUR_USERNAME.pythonanywhere.com/api/contact', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    
    if (response.ok) {
      status.textContent = '✅ ' + result.message;
      form.reset();
    } else {
      status.textContent = '❌ ' + result.detail;
    }
  } catch (error) {
    status.textContent = '❌ Network error. Please try again.';
  }
});
</script>
```

### React Example

```jsx
import { useState } from 'react';

function ContactForm() {
  const [formData, setFormData] = useState({
    name: '', email: '', subject: '', message: '', honeypot: ''
  });
  const [status, setStatus] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('Sending...');
    
    try {
      const response = await fetch('https://YOUR_USERNAME.pythonanywhere.com/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const result = await response.json();
      
      if (response.ok) {
        setStatus('✅ ' + result.message);
        setFormData({ name: '', email: '', subject: '', message: '', honeypot: '' });
      } else {
        setStatus('❌ ' + result.detail);
      }
    } catch (error) {
      setStatus('❌ Network error. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input 
        type="text" 
        placeholder="Name" 
        value={formData.name}
        onChange={(e) => setFormData({...formData, name: e.target.value})}
        required 
      />
      <input 
        type="email" 
        placeholder="Email" 
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
        required 
      />
      <input 
        type="text" 
        placeholder="Subject" 
        value={formData.subject}
        onChange={(e) => setFormData({...formData, subject: e.target.value})}
        required 
      />
      <textarea 
        placeholder="Message" 
        value={formData.message}
        onChange={(e) => setFormData({...formData, message: e.target.value})}
        required 
      />
      <input 
        type="text" 
        name="honeypot" 
        style={{display: 'none'}}
        value={formData.honeypot}
        onChange={(e) => setFormData({...formData, honeypot: e.target.value})}
        tabIndex="-1"
        autoComplete="off"
      />
      <button type="submit">Send</button>
      {status && <p>{status}</p>}
    </form>
  );
}
```

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

## 📝 License

Free to use for your portfolio!

## 💡 Tips

- Test locally first before deploying
- Keep your `.env` file secret (never commit to Git)
- Click "Extend" every 3 months on PythonAnywhere
- Monitor your inbox for messages!