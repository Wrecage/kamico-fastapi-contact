# Kamico Contact Form API - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Security Features](#security-features)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Format](#requestresponse-format)
5. [Error Handling](#error-handling)
6. [Integration Guide](#integration-guide)
7. [React + TypeScript + Sanity CMS Integration](#react--typescript--sanity-cms-integration)
8. [Testing](#testing)

---

## Overview

**Kamico Contact Form API** is a production-ready FastAPI service for handling contact form submissions with built-in security, validation, and email delivery.

### Key Features
- ✅ **CORS Protection** - Only whitelisted domains can access
- ✅ **Rate Limiting** - Protection against spam (5 requests/hour per IP)
- ✅ **Spam Detection** - Keyword-based spam filtering
- ✅ **Honeypot Field** - Bot trap mechanism
- ✅ **Input Validation** - Comprehensive validation including international characters
- ✅ **SQL Injection Safe** - Uses Pydantic models (no raw SQL queries)
- ✅ **Email Delivery** - SMTP with HTML formatting
- ✅ **Structured Error Responses** - Easy to handle on frontend

### Technology Stack
- **Framework**: FastAPI 0.109.0
- **Validation**: Pydantic 2.5.3
- **Server**: Uvicorn 0.27.0
- **Email**: Python SMTP (Gmail compatible)

---

## Security Features

### 1. **CORS (Cross-Origin Resource Sharing)**
```python
# Only these domains can call the API
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,https://yourdomain.com
```

### 2. **Rate Limiting**
- **5 requests per hour** per IP address
- Prevents spam and DoS attacks
- Returns 429 status when limit exceeded

### 3. **Input Validation**
- All fields are validated server-side
- International characters supported (ñ, é, ü, etc.)
- Length constraints enforced
- Spam keywords detected

### 4. **Honeypot Field**
- Hidden field to trap bots
- If filled, submission is rejected

### 5. **SQL Injection Protection**
- ✅ **You are SAFE** - No raw SQL queries used
- Pydantic models handle all input sanitization
- Data is JSON encoded, not interpolated into SQL

---

## API Endpoints

### POST /api/contact
**Submit a contact form**

#### Request
```json
{
  "first_name": "Juan",
  "last_name": "Peñaloza",
  "email": "juan@example.com",
  "phone": "+1 (555) 123-4567",
  "location": "Mountain side north river",
  "subject": "Website Inquiry",
  "message": "I'm interested in your services...",
  "honeypot": ""
}
```

#### Success Response (200)
```json
{
  "success": true,
  "status": "success",
  "message": "Your message has been sent successfully!",
  "timestamp": "2024-01-24T10:30:45.123456"
}
```

#### Validation Error Response (422)
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "field": "first_name",
      "message": "Name contains invalid characters",
      "type": "value_error"
    }
  ]
}
```

#### Rate Limit Error (429)
```json
{
  "detail": "Too many requests. Please try again later."
}
```

#### Server Error (500)
```json
{
  "detail": "Failed to send message. Please try again."
}
```

### GET /health
**Health check endpoint**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-24T10:30:45.123456",
  "smtp_configured": true,
  "allowed_origins": 3
}
```

### GET /
**Root endpoint with API info**

```json
{
  "status": "online",
  "service": "Portfolio Contact Form API",
  "version": "1.0.0",
  "endpoints": {
    "contact": "/api/contact (POST)",
    "health": "/ (GET)"
  }
}
```

---

## Request/Response Format

### Field Validation Rules

| Field | Type | Min/Max | Rules |
|-------|------|---------|-------|
| first_name | String | 2-50 | Letters, spaces, hyphens, apostrophes (✅ supports ñ, é, ü) |
| last_name | String | 2-50 | Letters, spaces, hyphens, apostrophes (✅ supports ñ, é, ü) |
| email | Email | - | Valid email format (RFC 5321) |
| phone | String | 7-20 | +, digits, spaces, hyphens |
| street | String | 5+ | Any characters allowed |
| city | String | 2+ | Any characters allowed |
| state | String | 2+ | Any characters allowed |
| zip_code | String | 5-10 | Alphanumeric, spaces, hyphens |
| subject | String | 3-200 | Any characters, no spam keywords |
| message | String | 10-5000 | Any characters, no spam keywords |
| honeypot | String (optional) | - | Must be empty (bot trap) |

### Spam Keywords (Detected & Blocked)
- viagra, cialis, crypto, bitcoin
- lottery, winner, casino, pills
- investment, free money, work from home

---

## Error Handling

### Common HTTP Status Codes

| Code | Meaning | Handling |
|------|---------|----------|
| 200 | Success | Message sent successfully |
| 422 | Validation Error | Check `errors` array for field-specific issues |
| 429 | Rate Limited | Wait before retrying (5 req/hour limit) |
| 500 | Server Error | SMTP/email delivery failed |

### Frontend Error Handling Example
```javascript
if (response.status === 422) {
  const data = await response.json();
  data.errors.forEach(error => {
    console.log(`${error.field}: ${error.message}`);
  });
}
```

---

## Integration Guide

### Basic HTML/JavaScript

```html
<form id="contactForm">
  <input type="text" name="first_name" required>
  <input type="text" name="last_name" required>
  <input type="email" name="email" required>
  <!-- other fields -->
  <button type="submit">Send</button>
</form>

<script>
const API_URL = 'https://yourdomain.com/api/contact';

document.getElementById('contactForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData);
  
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    
    if (response.ok) {
      alert(result.message);
      e.target.reset();
    } else if (response.status === 422) {
      result.errors.forEach(error => {
        alert(`${error.field}: ${error.message}`);
      });
    }
  } catch (error) {
    alert('Network error: ' + error.message);
  }
});
</script>
```

---

## React + TypeScript + Sanity CMS Integration

### Project Structure (Best Practice)

```
src/
├── services/
│   └── contactFormService.ts          # API calls
├── types/
│   └── contactForm.types.ts           # Type definitions
├── hooks/
│   └── useContactForm.ts              # Custom hook
├── components/
│   ├── ContactForm.tsx                # Form component
│   └── ContactForm.module.css
└── pages/
    └── ContactPage.tsx                # Page using form
```

### Step 1: Type Definitions

**`src/types/contactForm.types.ts`**
```typescript
/**
 * Contact Form Types
 * Type-safe interfaces for form data and API responses
 */

export interface ContactFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  street: string;
  city: string;
  state: string;
  zip_code: string;
  subject: string;
  message: string;
  honeypot?: string;
}

export interface ValidationError {
  field: keyof ContactFormData;
  message: string;
  type: string;
}

export interface ApiErrorResponse {
  success: false;
  message: string;
  errors: ValidationError[];
}

export interface ApiSuccessResponse {
  success: true;
  status: 'success';
  message: string;
  timestamp: string;
}

export type ApiResponse = ApiSuccessResponse | ApiErrorResponse;

export interface ContactFormState {
  data: ContactFormData;
  loading: boolean;
  error: string | null;
  fieldErrors: Record<keyof ContactFormData, string | null>;
  success: boolean;
}
```

### Step 2: API Service

**`src/services/contactFormService.ts`**
```typescript
/**
 * Contact Form Service
 * Handles all API communication with the contact form backend
 */

import type { ContactFormData, ApiResponse } from '../types/contactForm.types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_ENDPOINT = `${API_BASE_URL}/api/contact`;
const HEALTH_ENDPOINT = `${API_BASE_URL}/health`;

interface FetchOptions {
  timeout?: number;
  retries?: number;
}

/**
 * Check if API is healthy and accessible
 */
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(HEALTH_ENDPOINT, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    return response.ok;
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
};

/**
 * Submit contact form data to API
 * @param formData - Complete contact form data
 * @param options - Fetch options (timeout, retries)
 * @returns API response with success/error information
 */
export const submitContactForm = async (
  formData: ContactFormData,
  options: FetchOptions = {}
): Promise<ApiResponse> => {
  const { timeout = 10000, retries = 1 } = options;

  const makeRequest = async (): Promise<Response> => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      return await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData),
        signal: controller.signal
      });
    } finally {
      clearTimeout(timeoutId);
    }
  };

  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await makeRequest();
      const data = await response.json();

      if (!response.ok) {
        return data;
      }

      return data;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      
      if (attempt < retries) {
        // Wait before retrying (exponential backoff)
        await new Promise(resolve => 
          setTimeout(resolve, Math.pow(2, attempt) * 1000)
        );
      }
    }
  }

  // All retries failed
  return {
    success: false,
    message: lastError?.message || 'Network error. Please try again.',
    errors: []
  };
};

/**
 * Validate form data client-side before sending
 * @param data - Form data to validate
 * @returns Object with validation results
 */
export const validateFormData = (
  data: ContactFormData
): { valid: boolean; errors: Record<string, string> } => {
  const errors: Record<string, string> = {};

  if (data.first_name.trim().length < 2) {
    errors.first_name = 'First name must be at least 2 characters';
  }

  if (data.last_name.trim().length < 2) {
    errors.last_name = 'Last name must be at least 2 characters';
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(data.email)) {
    errors.email = 'Please enter a valid email address';
  }

  if (data.phone.trim().length < 7) {
    errors.phone = 'Please enter a valid phone number';
  }

  if (data.subject.trim().length < 3) {
    errors.subject = 'Subject must be at least 3 characters';
  }

  if (data.message.trim().length < 10) {
    errors.message = 'Message must be at least 10 characters';
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
};
```

### Step 3: Custom Hook

**`src/hooks/useContactForm.ts`**
```typescript
/**
 * useContactForm Hook
 * Manages contact form state and submission logic
 */

import { useState, useCallback } from 'react';
import {
  submitContactForm,
  validateFormData
} from '../services/contactFormService';
import type {
  ContactFormData,
  ContactFormState,
  ValidationError
} from '../types/contactForm.types';

const initialFormData: ContactFormData = {
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  street: '',
  city: '',
  state: '',
  zip_code: '',
  subject: '',
  message: '',
  honeypot: ''
};

const initialFieldErrors: Record<keyof ContactFormData, string | null> = {
  first_name: null,
  last_name: null,
  email: null,
  phone: null,
  street: null,
  city: null,
  state: null,
  zip_code: null,
  subject: null,
  message: null,
  honeypot: null
};

export const useContactForm = () => {
  const [state, setState] = useState<ContactFormState>({
    data: initialFormData,
    loading: false,
    error: null,
    fieldErrors: initialFieldErrors,
    success: false
  });

  /**
   * Update individual form field
   */
  const setField = useCallback(
    (field: keyof ContactFormData, value: string) => {
      setState(prev => ({
        ...prev,
        data: { ...prev.data, [field]: value },
        fieldErrors: { ...prev.fieldErrors, [field]: null },
        error: null
      }));
    },
    []
  );

  /**
   * Handle form submission
   */
  const handleSubmit = useCallback(
    async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();

      // Client-side validation
      const { valid, errors: validationErrors } = validateFormData(state.data);

      if (!valid) {
        setState(prev => ({
          ...prev,
          fieldErrors: {
            ...prev.fieldErrors,
            ...Object.entries(validationErrors).reduce(
              (acc, [key, value]) => {
                acc[key as keyof ContactFormData] = value;
                return acc;
              },
              {} as Record<keyof ContactFormData, string>
            )
          },
          error: 'Please fix the errors below'
        }));
        return;
      }

      setState(prev => ({
        ...prev,
        loading: true,
        error: null,
        success: false
      }));

      try {
        const response = await submitContactForm(state.data);

        if (response.success) {
          setState(prev => ({
            ...prev,
            loading: false,
            success: true,
            data: initialFormData,
            fieldErrors: initialFieldErrors,
            error: null
          }));

          // Clear success message after 5 seconds
          setTimeout(() => {
            setState(prev => ({ ...prev, success: false }));
          }, 5000);
        } else {
          // Server validation errors
          const newFieldErrors = { ...initialFieldErrors };

          if ('errors' in response && Array.isArray(response.errors)) {
            response.errors.forEach((err: ValidationError) => {
              newFieldErrors[err.field] = err.message;
            });
          }

          setState(prev => ({
            ...prev,
            loading: false,
            error: response.message || 'Failed to submit form',
            fieldErrors: newFieldErrors,
            success: false
          }));
        }
      } catch (err) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: 'Network error. Please try again.',
          success: false
        }));
      }
    },
    [state.data]
  );

  /**
   * Reset form to initial state
   */
  const reset = useCallback(() => {
    setState({
      data: initialFormData,
      loading: false,
      error: null,
      fieldErrors: initialFieldErrors,
      success: false
    });
  }, []);

  return {
    ...state,
    setField,
    handleSubmit,
    reset
  };
};
```

### Step 4: React Contact Form Component

**`src/components/ContactForm.tsx`**
```typescript
/**
 * ContactForm Component
 * Renders contact form with validation feedback
 */

import React from 'react';
import { useContactForm } from '../hooks/useContactForm';
import styles from './ContactForm.module.css';

export const ContactForm: React.FC = () => {
  const {
    data,
    loading,
    error,
    fieldErrors,
    success,
    setField,
    handleSubmit,
    reset
  } = useContactForm();

  return (
    <div className={styles.container}>
      <h1>Get In Touch</h1>
      <p className={styles.subtitle}>We'd love to hear from you</p>

      {success && (
        <div className={styles.successMessage}>
          ✅ {' '}
          Your message has been sent successfully! We'll get back to you soon.
        </div>
      )}

      {error && (
        <div className={styles.errorMessage}>
          ❌ {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Personal Information Section */}
        <fieldset className={styles.fieldset}>
          <legend>Personal Information</legend>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="firstName">
                First Name *
              </label>
              <input
                id="firstName"
                type="text"
                name="first_name"
                value={data.first_name}
                onChange={(e) => setField('first_name', e.target.value)}
                placeholder="Juan"
                disabled={loading}
                className={fieldErrors.first_name ? styles.inputError : ''}
                required
              />
              {fieldErrors.first_name && (
                <span className={styles.fieldErrorMessage}>
                  {fieldErrors.first_name}
                </span>
              )}
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="lastName">
                Last Name *
              </label>
              <input
                id="lastName"
                type="text"
                name="last_name"
                value={data.last_name}
                onChange={(e) => setField('last_name', e.target.value)}
                placeholder="Peñaloza"
                disabled={loading}
                className={fieldErrors.last_name ? styles.inputError : ''}
                required
              />
              {fieldErrors.last_name && (
                <span className={styles.fieldErrorMessage}>
                  {fieldErrors.last_name}
                </span>
              )}
            </div>
          </div>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="email">
                Email *
              </label>
              <input
                id="email"
                type="email"
                name="email"
                value={data.email}
                onChange={(e) => setField('email', e.target.value)}
                placeholder="juan@example.com"
                disabled={loading}
                className={fieldErrors.email ? styles.inputError : ''}
                required
              />
              {fieldErrors.email && (
                <span className={styles.fieldErrorMessage}>
                  {fieldErrors.email}
                </span>
              )}
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="phone">
                Phone *
              </label>
              <input
                id="phone"
                type="tel"
                name="phone"
                value={data.phone}
                onChange={(e) => setField('phone', e.target.value)}
                placeholder="+1 (555) 123-4567"
                disabled={loading}
                className={fieldErrors.phone ? styles.inputError : ''}
                required
              />
              {fieldErrors.phone && (
                <span className={styles.fieldErrorMessage}>
                  {fieldErrors.phone}
                </span>
              )}
            </div>
          </div>
        </fieldset>

        {/* Address Section */}
        <fieldset className={styles.fieldset}>
          <legend>Address</legend>

          <div className={styles.formGroup}>
            <label htmlFor="street">
              Street Address *
            </label>
            <input
              id="street"
              type="text"
              name="street"
              value={data.street}
              onChange={(e) => setField('street', e.target.value)}
              placeholder="123 Main Street"
              disabled={loading}
              className={fieldErrors.street ? styles.inputError : ''}
              required
            />
            {fieldErrors.street && (
              <span className={styles.fieldErrorMessage}>
                {fieldErrors.street}
              </span>
            )}
          </div>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="city">
                City *
              </label>
              <input
                id="city"
                type="text"
                name="city"
                value={data.city}
                onChange={(e) => setField('city', e.target.value)}
                placeholder="New York"
                disabled={loading}
                className={fieldErrors.city ? styles.inputError : ''}
                required
              />
              {fieldErrors.city && (
                <span className={styles.fieldErrorMessage}>
                  {fieldErrors.city}
                </span>
              )}
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="state">
                State/Province *
              </label>
              <input
                id="state"
                type="text"
                name="state"
                value={data.state}
                onChange={(e) => setField('state', e.target.value)}
                placeholder="NY"
                disabled={loading}
                className={fieldErrors.state ? styles.inputError : ''}
                required
              />
              {fieldErrors.state && (
                <span className={styles.fieldErrorMessage}>
                  {fieldErrors.state}
                </span>
              )}
            </div>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="zipCode">
              ZIP / Postal Code *
            </label>
            <input
              id="zipCode"
              type="text"
              name="zip_code"
              value={data.zip_code}
              onChange={(e) => setField('zip_code', e.target.value)}
              placeholder="10001"
              disabled={loading}
              className={fieldErrors.zip_code ? styles.inputError : ''}
              required
            />
            {fieldErrors.zip_code && (
              <span className={styles.fieldErrorMessage}>
                {fieldErrors.zip_code}
              </span>
            )}
          </div>
        </fieldset>

        {/* Message Section */}
        <fieldset className={styles.fieldset}>
          <legend>Message</legend>

          <div className={styles.formGroup}>
            <label htmlFor="subject">
              Subject *
            </label>
            <input
              id="subject"
              type="text"
              name="subject"
              value={data.subject}
              onChange={(e) => setField('subject', e.target.value)}
              placeholder="Website Inquiry"
              disabled={loading}
              className={fieldErrors.subject ? styles.inputError : ''}
              required
            />
            {fieldErrors.subject && (
              <span className={styles.fieldErrorMessage}>
                {fieldErrors.subject}
              </span>
            )}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="message">
              Message *
            </label>
            <textarea
              id="message"
              name="message"
              value={data.message}
              onChange={(e) => setField('message', e.target.value)}
              placeholder="Tell us about your project..."
              disabled={loading}
              className={fieldErrors.message ? styles.inputError : ''}
              rows={6}
              required
            />
            {fieldErrors.message && (
              <span className={styles.fieldErrorMessage}>
                {fieldErrors.message}
              </span>
            )}
          </div>
        </fieldset>

        {/* Honeypot (hidden field for bot protection) */}
        <input
          type="text"
          name="honeypot"
          value={data.honeypot}
          onChange={(e) => setField('honeypot', e.target.value)}
          style={{ display: 'none' }}
          tabIndex={-1}
          autoComplete="off"
        />

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className={styles.submitButton}
        >
          {loading ? 'Sending...' : 'Send Message'}
        </button>
      </form>
    </div>
  );
};
```

### Step 5: CSS Module

**`src/components/ContactForm.module.css`**
```css
.container {
  max-width: 700px;
  margin: 0 auto;
  padding: 40px 20px;
}

.container h1 {
  font-size: 28px;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.subtitle {
  color: #666;
  margin-bottom: 30px;
  font-size: 16px;
}

.successMessage {
  background: #d4edda;
  color: #155724;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #c3e6cb;
}

.errorMessage {
  background: #f8d7da;
  color: #721c24;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #f5c6cb;
}

.fieldset {
  border: none;
  margin-bottom: 30px;
  padding: 0;
}

.fieldset legend {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #1a1a1a;
  padding: 0;
}

.formRow {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

@media (max-width: 600px) {
  .formRow {
    grid-template-columns: 1fr;
  }
}

.formGroup {
  display: flex;
  flex-direction: column;
}

.formGroup label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.formGroup input,
.formGroup textarea {
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 15px;
  font-family: inherit;
  transition: border-color 0.3s;
}

.formGroup input:focus,
.formGroup textarea:focus {
  outline: none;
  border-color: #667eea;
}

.formGroup input:disabled,
.formGroup textarea:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.inputError {
  border-color: #dc3545 !important;
}

.fieldErrorMessage {
  color: #dc3545;
  font-size: 12px;
  margin-top: 4px;
}

.submitButton {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.submitButton:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
}

.submitButton:active:not(:disabled) {
  transform: translateY(0);
}

.submitButton:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}
```

### Step 6: Using in a Page (Sanity CMS Integration)

**`src/pages/ContactPage.tsx`**
```typescript
/**
 * ContactPage Component
 * Integrates contact form with Sanity CMS content
 */

import React, { useEffect, useState } from 'react';
import { ContactForm } from '../components/ContactForm';
import { checkApiHealth } from '../services/contactFormService';
import { client } from '../lib/sanity'; // Your Sanity client

interface PageContent {
  title: string;
  description: string;
  content: unknown;
}

export const ContactPage: React.FC = () => {
  const [pageContent, setPageContent] = useState<PageContent | null>(null);
  const [apiHealthy, setApiHealthy] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadContent = async () => {
      try {
        // Fetch page content from Sanity CMS
        const query = `
          *[_type == "contactPage"][0] {
            title,
            description,
            content
          }
        `;

        const content = await client.fetch(query);
        setPageContent(content);

        // Check API health
        const healthy = await checkApiHealth();
        setApiHealthy(healthy);
      } catch (error) {
        console.error('Failed to load page content:', error);
      } finally {
        setLoading(false);
      }
    };

    loadContent();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      {pageContent && (
        <header>
          <h1>{pageContent.title}</h1>
          <p>{pageContent.description}</p>
        </header>
      )}

      {!apiHealthy && (
        <div style={{ 
          padding: '15px', 
          background: '#fff3cd', 
          color: '#856404',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          ⚠️ API is currently unavailable. Please try again later.
        </div>
      )}

      <ContactForm />
    </div>
  );
};
```

### Step 7: Environment Configuration

**`.env.local`**
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=10000
```

**`.env.production`**
```bash
REACT_APP_API_URL=https://yourdomain.com
REACT_APP_API_TIMEOUT=10000
```

---

## Testing

### Manual Testing Checklist

- [ ] Submit with valid data → Success
- [ ] Submit with special characters (ñ, é) → Success
- [ ] Submit with invalid email → Error
- [ ] Submit with short message → Error
- [ ] Submit honeypot filled → Rejected
- [ ] Submit 6 times in 1 hour → 429 error
- [ ] Check CORS headers (origin mismatch) → 403
- [ ] Network timeout → Retry and handle gracefully

### Unit Test Example (Jest + React Testing Library)

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ContactForm } from './ContactForm';
import * as contactService from '../services/contactFormService';

jest.mock('../services/contactFormService');

describe('ContactForm', () => {
  it('should display validation error for short name', async () => {
    render(<ContactForm />);

    fireEvent.change(screen.getByLabelText(/first name/i), {
      target: { value: 'J' }
    });

    fireEvent.click(screen.getByText(/send message/i));

    await waitFor(() => {
      expect(screen.getByText(/at least 2 characters/i)).toBeInTheDocument();
    });
  });

  it('should submit form with valid data', async () => {
    const mockSubmit = jest.fn().mockResolvedValue({
      success: true,
      message: 'Success'
    });

    (contactService.submitContactForm as jest.Mock) = mockSubmit;

    render(<ContactForm />);

    fireEvent.change(screen.getByLabelText(/first name/i), {
      target: { value: 'Juan' }
    });

    fireEvent.click(screen.getByText(/send message/i));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalled();
    });
  });
});
```

---

## Security Summary

| Threat | Protection |
|--------|-----------|
| SQL Injection | ✅ No raw SQL (Pydantic models) |
| XSS | ✅ JSON encoded responses |
| CSRF | ✅ CORS origin validation |
| Bot Spam | ✅ Honeypot + rate limiting |
| DDoS | ✅ Rate limiting (5 req/hr) |
| Invalid Data | ✅ Comprehensive server-side validation |

---

## Support & Questions

For issues or questions:
1. Check error response format (422 errors include field details)
2. Verify CORS origin is in `ALLOWED_ORIGINS`
3. Check rate limit (429 = too many requests)
4. Verify API is running: `GET /health`

---

**Last Updated**: January 24, 2026  
**API Version**: 1.0.0
