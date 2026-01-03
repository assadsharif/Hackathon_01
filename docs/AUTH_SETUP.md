# Authentication Setup Guide

**Version**: Tier 1 (Lightweight Signup)
**Status**: UI Complete - Email Service Configuration Required

---

## Overview

The signup/signin functionality has been implemented with a progressive enhancement approach:

- **Tier 0 (Anonymous)**: Works now - ChatKit widget with browser-local storage
- **Tier 1 (Lightweight)**: Email verification for cross-device sync
- **Tier 2 (Future)**: OAuth integration (Google, GitHub, Microsoft)
- **Tier 3 (Future)**: Premium features

**Current Status**: Tier 1 UI is complete. Email service configuration required for full functionality.

---

## UI Components Implemented ✅

### 1. Sign Up / Sign In Button (Navbar)

**Location**: Top-right of navigation bar

**Features**:
- Shows "Sign Up / Sign In" when not authenticated
- Shows user email + "Sign Out" button when authenticated
- Session persistence via localStorage

**Component**: `physical-ai-book/src/components/Auth/AuthButton.tsx`

### 2. Signup Modal

**Features**:
- Email input with validation
- Privacy consent checkbox (required)
- Two-step flow: signup → verification sent
- Resend verification email option
- Responsive design (mobile/tablet/desktop)
- Dark mode support

**Component**: `physical-ai-book/src/components/Auth/SignupModal.tsx`

### 3. Email Verification Page

**URL**: `http://localhost:3000/Hackathon_01/verify?token=xyz`

**Features**:
- Handles verification links from email
- Auto-saves session token on success
- Auto-redirects to home page
- Error handling with helpful instructions

**Component**: `physical-ai-book/src/pages/verify.tsx`

---

## Backend API Integration ✅

All API endpoints are already implemented in the backend:

### Signup Endpoint
```
POST http://localhost:8000/api/v1/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "consent_data_storage": true,
  "migrate_session": false
}
```

**Response**:
```json
{
  "status": "verification_sent"
}
```

### Verify Endpoint
```
POST http://localhost:8000/api/v1/auth/verify
Content-Type: application/json

{
  "token": "verification-token-from-email"
}
```

**Response**:
```json
{
  "session_token": "jwt-token-here",
  "user_profile": {
    "email": "user@example.com",
    "tier": "lightweight"
  }
}
```

### Session Check Endpoint
```
GET http://localhost:8000/api/v1/auth/session-check
Authorization: Bearer <session-token>
```

---

## Email Service Configuration ⚠️

**Required**: SMTP configuration for email verification to work.

### Step 1: Configure Backend .env

Edit `chatkit-widget-implementation/backend/.env`:

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use App Password, not regular password
```

### Step 2: Gmail App Password Setup

If using Gmail:

1. Go to Google Account Settings
2. Security → 2-Step Verification (enable if not enabled)
3. Search for "App passwords"
4. Generate app password for "Mail"
5. Copy the 16-character password
6. Use this in `SMTP_PASSWORD`

### Step 3: Verify Email Service

```bash
cd chatkit-widget-implementation/backend
source venv/bin/activate
python -c "from app.services.email_service import EmailService; import asyncio; asyncio.run(EmailService().send_verification_email('test@example.com', 'test-token'))"
```

**Expected**: Email sent successfully (check logs)

---

## Testing Without Email (Development) 🔧

For testing without configuring SMTP:

### Option 1: Use Backend Logs

1. User submits signup
2. Check backend console/logs for verification token
3. Manually construct verification URL:
   ```
   http://localhost:3000/Hackathon_01/verify?token=<token-from-logs>
   ```
4. Open URL in browser

### Option 2: Mock Email Service

Edit `backend/app/services/email_service.py`:

```python
async def send_verification_email(self, email: str, token: str):
    verification_url = f"http://localhost:3000/Hackathon_01/verify?token={token}"

    # Mock: Print to console instead of sending email
    print(f"""
    ==================== VERIFICATION EMAIL ====================
    To: {email}
    Subject: Verify your email for Physical AI Book

    Click here to verify your email:
    {verification_url}

    Token expires in 10 minutes.
    ===========================================================
    """)

    return True  # Pretend email was sent
```

---

## Testing Signup Flow End-to-End

### Prerequisites
- ✅ Backend running: http://localhost:8000
- ✅ Docusaurus running: http://localhost:3000/Hackathon_01/
- ⚠️ Email service configured (or using mock)

### Test Steps

#### 1. Open Docusaurus Site
```
http://localhost:3000/Hackathon_01/
```

#### 2. Click "Sign Up / Sign In" (top-right navbar)

#### 3. Fill Signup Form
- Email: test@example.com
- Check consent checkbox
- Click "Sign Up"

**Expected**:
- Loading state shown
- Success message: "Check Your Email!"
- Instructions displayed

#### 4. Get Verification Token

**If email configured**:
- Check email inbox
- Click verification link

**If using mock/logs**:
- Check backend console
- Copy verification URL
- Paste in browser

#### 5. Verify Email

URL opens: `http://localhost:3000/Hackathon_01/verify?token=xyz`

**Expected**:
- "Verifying your email..." (spinner)
- "Email Verified!" (success icon)
- Auto-redirect to home page after 3 seconds

#### 6. Verify Authentication Status

After redirect:
- Top-right navbar shows: email + "Sign Out" button
- Session persists (refresh page to confirm)

---

## Troubleshooting

### Issue: "Sign Up / Sign In" button not visible

**Solution**:
1. Rebuild Docusaurus: `npm run build`
2. Restart dev server: `npm start`
3. Clear browser cache (Ctrl+Shift+Delete)

### Issue: Modal doesn't open when clicking button

**Check**:
1. Browser console for errors (F12)
2. Ensure React is rendering properly
3. Check z-index conflicts with other components

### Issue: "Invalid email address" error

**Check**:
- Email format is valid (user@domain.com)
- No spaces in email field

### Issue: "You must consent to data storage"

**Check**:
- Consent checkbox is checked
- Checkbox is not disabled

### Issue: Signup succeeds but no email received

**Check**:
1. SMTP configuration in backend .env
2. Backend logs for email sending errors
3. Spam folder in email
4. Use mock email for testing (see above)

### Issue: Verification link expired

**Cause**: Tokens expire after 10 minutes

**Solution**:
- Click "Resend Verification Email" in modal
- Or sign up again

### Issue: Verification fails with "Invalid token"

**Check**:
1. Token is complete (full URL copied)
2. Token hasn't expired (10 min limit)
3. Token hasn't been used already

---

## Session Management

### Where is the session stored?

**Frontend**: localStorage key `chatkit_session_token`

**Backend**: Database table `sessions`

### How long does the session last?

**Access Token**: 15 minutes
**Refresh Token**: 7 days

### How to sign out?

Click "Sign Out" button in navbar:
1. Clears `chatkit_session_token` from localStorage
2. Reloads page (resets to anonymous mode)

### How to check if authenticated?

```javascript
const token = localStorage.getItem('chatkit_session_token');
if (token) {
  // User is authenticated
}
```

---

## Next Steps (Tier 2 OAuth)

After Tier 1 is working:

### 1. Add OAuth Providers

**Google Sign-In**:
- Create Google Cloud project
- Enable Google Sign-In API
- Add OAuth credentials
- Configure backend `/api/v1/auth/oauth/google`

**GitHub Sign-In**:
- Create GitHub OAuth App
- Configure callback URL
- Add backend `/api/v1/auth/oauth/github`

**Microsoft Sign-In**:
- Create Azure AD app registration
- Configure OAuth
- Add backend `/api/v1/auth/oauth/microsoft`

### 2. Update UI

Add OAuth buttons to SignupModal:
- "Continue with Google"
- "Continue with GitHub"
- "Continue with Microsoft"

### 3. Session Migration

Implement anonymous → authenticated session migration:
- Preserve conversation history from Tier 0
- Merge browser-local data to server

---

## Design Reference

All authentication design patterns documented in:

- `.claude/skills/signup-personalization/SKILL.md` (11,899 lines)
- `.claude/skills/signup-personalization/patterns.md` (17,196 lines)
- `.claude/mcp/better-auth/README.md` (12,669 lines)

**Design Principles**:
- Progressive enhancement (Tier 0 → 1 → 2 → 3)
- Privacy-first (GDPR, CCPA, FERPA compliant)
- Zero friction (anonymous access always available)
- Clear value proposition (sync, personalization, analytics)

---

## Production Deployment

Before deploying to production:

### Backend
- [ ] Configure production SMTP (SendGrid, AWS SES, etc.)
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS only cookies
- [ ] Configure CORS for production domain
- [ ] Set up email delivery monitoring

### Frontend
- [ ] Update API URLs to production backend
- [ ] Update verification URL in emails to production domain
- [ ] Configure production base URL in docusaurus.config.ts
- [ ] Test email delivery in production

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
