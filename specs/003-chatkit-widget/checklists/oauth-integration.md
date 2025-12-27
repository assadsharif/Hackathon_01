# OAuth Integration Checklist (Better-Auth)

**Document Type**: Implementation Checklist
**User Story**: US3 (Progressive Signup)
**Phase**: 6 (Design Specification)
**Created**: 2025-12-26

---

## Overview

This checklist ensures correct implementation of OAuth authentication (Google, GitHub, Microsoft) for Tier 1 → Tier 2 upgrades using the Better-Auth authentication library.

**Requirements**:
- FR-015: Widget MUST support OAuth authentication (Google, GitHub, Microsoft) for Tier 2 (full profile)
- FR-016: Widget MUST merge browser-local sessions with server-side sessions on tier upgrade
- NFR-013: Widget MUST NOT share data with third parties (OAuth providers only for authentication)

**Pattern Reference**: Pattern 3 (Session Continuity), Pattern 1 (Progressive Enhancement Signup) from `.claude/skills/signup-personalization/`

---

## Pre-Implementation Review

### Design Artifacts

- [ ] Read Pattern 3 (Session Continuity) in `.claude/skills/chatkit-widget/patterns.md` lines 267-416
- [ ] Review authentication_completed event schema (SKILL.md lines 190-202)
- [ ] Review tier upgrade guide (integration/tier-upgrades.md) - OAuth upgrade flow
- [ ] Review signup-personalization patterns (`.claude/skills/signup-personalization/patterns.md`)
- [ ] Review Better-Auth documentation (Phase 7+ dependency)

---

## OAuth Provider Setup

### Google OAuth Configuration

**Required**: Google Cloud Console OAuth 2.0 Client ID

**Setup Steps** (for Phase 7+ implementation):

- [ ] Create Google Cloud project: `physical-ai-book-chatkit`
- [ ] Enable Google+ API and OAuth Consent Screen
- [ ] Configure OAuth consent screen:
  - App name: "Physical AI & Humanoid Robotics - ChatKit"
  - User support email: admin@physical-ai-book.com
  - Authorized domains: physical-ai-book.com
  - Scopes: `openid`, `email`, `profile` (minimal scope)
- [ ] Create OAuth 2.0 Client ID:
  - Application type: Web application
  - Authorized JavaScript origins: `https://physical-ai-book.com`
  - Authorized redirect URIs: `https://physical-ai-book.com/api/v1/auth/oauth/google/callback`
- [ ] Save Client ID and Client Secret to environment variables:
  ```bash
  GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
  GOOGLE_CLIENT_SECRET=your-client-secret
  ```

**Security**:
- [ ] NEVER commit Client Secret to version control (use .env files)
- [ ] Rotate Client Secret every 90 days (security best practice)
- [ ] Use PKCE (Proof Key for Code Exchange) for mobile/SPA flows

---

### GitHub OAuth Configuration

**Required**: GitHub OAuth App

**Setup Steps** (for Phase 7+ implementation):

- [ ] Navigate to GitHub Settings → Developer settings → OAuth Apps → New OAuth App
- [ ] Configure OAuth app:
  - Application name: "Physical AI & Humanoid Robotics - ChatKit"
  - Homepage URL: `https://physical-ai-book.com`
  - Authorization callback URL: `https://physical-ai-book.com/api/v1/auth/oauth/github/callback`
- [ ] Save Client ID and Client Secret to environment variables:
  ```bash
  GITHUB_CLIENT_ID=your-github-client-id
  GITHUB_CLIENT_SECRET=your-github-client-secret
  ```
- [ ] Request scopes: `user:email` (minimal scope for email address)

**Security**:
- [ ] Enable "Require users to authorize each time" for sensitive applications (optional)
- [ ] Verify webhook signatures if using GitHub webhooks

---

### Microsoft OAuth Configuration

**Required**: Microsoft Azure AD App Registration

**Setup Steps** (for Phase 7+ implementation):

- [ ] Navigate to Azure Portal → Azure Active Directory → App registrations → New registration
- [ ] Configure app registration:
  - Name: "Physical AI & Humanoid Robotics - ChatKit"
  - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
  - Redirect URI: Web → `https://physical-ai-book.com/api/v1/auth/oauth/microsoft/callback`
- [ ] Navigate to Certificates & secrets → New client secret
- [ ] Save Application (client) ID and Client Secret to environment variables:
  ```bash
  MICROSOFT_CLIENT_ID=your-azure-app-id
  MICROSOFT_CLIENT_SECRET=your-azure-client-secret
  ```
- [ ] Configure API permissions:
  - Microsoft Graph API: `openid`, `email`, `profile` (delegated permissions)

**Security**:
- [ ] Set client secret expiration to 90 days (auto-rotate)
- [ ] Enable Conditional Access policies for enterprise users (optional)

---

## Better-Auth Library Integration

### Installation (Phase 7+ Implementation)

**Better-Auth**: Modern TypeScript-first authentication library

**Installation**:
```bash
npm install better-auth
```

**Dependencies**:
- `@better-auth/google` - Google OAuth provider
- `@better-auth/github` - GitHub OAuth provider
- `@better-auth/microsoft` - Microsoft OAuth provider

---

### Better-Auth Configuration

**Configuration File**: `server/auth.config.ts` (design-level)

```typescript
// Design-level configuration (not runtime code)
import { createAuth } from 'better-auth';

export const auth = createAuth({
  // Database connection (for user accounts, sessions)
  database: {
    type: 'postgresql',
    connectionString: process.env.DATABASE_URL
  },

  // OAuth providers
  providers: [
    {
      type: 'google',
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      redirectUri: '/api/v1/auth/oauth/google/callback'
    },
    {
      type: 'github',
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
      redirectUri: '/api/v1/auth/oauth/github/callback'
    },
    {
      type: 'microsoft',
      clientId: process.env.MICROSOFT_CLIENT_ID,
      clientSecret: process.env.MICROSOFT_CLIENT_SECRET,
      redirectUri: '/api/v1/auth/oauth/microsoft/callback'
    }
  ],

  // Session management
  session: {
    strategy: 'jwt',  // Use JWT tokens (stateless)
    maxAge: 30 * 24 * 60 * 60,  // 30 days
    secureCookie: true,  // HTTPS only
    sameSite: 'lax'  // CSRF protection
  },

  // Security
  security: {
    csrfProtection: true,
    rateLimit: {
      windowMs: 15 * 60 * 1000,  // 15 minutes
      max: 5  // Max 5 OAuth attempts per window
    }
  }
});
```

---

## OAuth Flow Implementation

### Step 1: Initiate OAuth (Widget → Server)

**Trigger**: User clicks "Sign in with Google" button in widget

**Widget Behavior**:
1. Widget emits `signup_initiated` event:
```json
{
  "event": "signup_initiated",
  "flow": {
    "type": "progressive_signup",
    "current_tier": "lightweight",
    "target_tier": "full",
    "trigger": "oauth_signin_google"
  }
}
```

2. Widget redirects to OAuth authorization endpoint:
```typescript
// Design-level redirect logic
function initiateOAuthSignin(provider: 'google' | 'github' | 'microsoft', userId: string) {
  const redirectUri = `${window.location.origin}/chatkit`;
  const state = generateSecureState(userId);  // CSRF protection

  // Redirect to Better-Auth OAuth endpoint
  window.location.href = `/api/v1/auth/oauth/${provider}?redirect_uri=${redirectUri}&state=${state}`;
}

function generateSecureState(userId: string): string {
  // CRITICAL: State parameter prevents CSRF attacks
  const nonce = crypto.randomUUID();
  const payload = { userId, nonce, timestamp: Date.now() };
  return btoa(JSON.stringify(payload));
}
```

---

### Step 2: OAuth Provider Authorization

**Server Behavior** (Better-Auth handles this automatically):

1. Server receives OAuth request from widget
2. Server generates authorization URL with OAuth provider (Google/GitHub/Microsoft)
3. Server includes PKCE code challenge (for SPA security)
4. Server redirects user to OAuth provider consent screen

**Google Consent Screen Example**:
```
┌───────────────────────────────────────────────┐
│  Sign in with Google                          │
│                                               │
│  Physical AI & Humanoid Robotics - ChatKit   │
│  wants to:                                    │
│                                               │
│  ✓ Know who you are on Google                │
│  ✓ View your email address                   │
│                                               │
│  [Cancel]  [Allow]                            │
└───────────────────────────────────────────────┘
```

**User Actions**:
- **Allow** → OAuth provider redirects to callback URL with authorization code
- **Cancel** → OAuth provider redirects to callback URL with `error=access_denied`

---

### Step 3: OAuth Callback (Server)

**Callback URL**: `/api/v1/auth/oauth/{provider}/callback`

**Server Behavior** (Better-Auth):

1. Receive authorization code from OAuth provider:
```
GET /api/v1/auth/oauth/google/callback?code=google-auth-code&state=base64-encoded-state
```

2. Verify `state` parameter matches (CSRF protection):
```typescript
// Design-level verification
function verifyOAuthState(receivedState: string, expectedUserId: string): boolean {
  const decoded = JSON.parse(atob(receivedState));
  return decoded.userId === expectedUserId && (Date.now() - decoded.timestamp < 5 * 60 * 1000);  // 5 min expiry
}
```

3. Exchange authorization code for OAuth access token:
```typescript
// Better-Auth handles this automatically
const response = await fetch('https://oauth2.googleapis.com/token', {
  method: 'POST',
  body: JSON.stringify({
    code: authorizationCode,
    client_id: process.env.GOOGLE_CLIENT_ID,
    client_secret: process.env.GOOGLE_CLIENT_SECRET,
    redirect_uri: '/api/v1/auth/oauth/google/callback',
    grant_type: 'authorization_code'
  })
});

const { access_token, id_token } = await response.json();
```

4. Retrieve user profile from OAuth provider:
```typescript
const profileResponse = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
  headers: { Authorization: `Bearer ${access_token}` }
});

const { email, name, picture } = await profileResponse.json();
```

5. Link OAuth provider to existing user account (Tier 1 → Tier 2 upgrade):
```typescript
// Design-level user linking
async function linkOAuthProvider(userId: string, provider: string, oauthProfile: OAuthProfile) {
  // Update user record in database
  await db.users.update({
    where: { id: userId },
    data: {
      oauth_providers: { push: provider },  // Add "google" to providers array
      oauth_emails: { push: oauthProfile.email },
      tier: 'full',  // Upgrade to Tier 2
      profile_picture: oauthProfile.picture  // Optional: use OAuth profile picture
    }
  });

  // Generate new JWT with tier = "full"
  const sessionToken = jwt.sign(
    { userId, tier: 'full', oauth: true },
    process.env.JWT_SECRET,
    { expiresIn: '30d' }
  );

  return { sessionToken, tier: 'full' };
}
```

6. Redirect back to widget with session token:
```
GET /chatkit?session_token=jwt-token&tier=full
```

---

### Step 4: Widget Receives OAuth Callback

**Widget Behavior**:

1. Parse URL parameters (session_token, tier):
```typescript
// Design-level callback handling
window.addEventListener('load', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const sessionToken = urlParams.get('session_token');
  const tier = urlParams.get('tier');

  if (sessionToken && tier) {
    handleOAuthCallback(sessionToken, tier);
  }
});

function handleOAuthCallback(sessionToken: string, tier: string) {
  // Store session token in LocalStorage
  localStorage.setItem('session_token', sessionToken);

  // Emit authentication_completed event
  emitEvent({
    event: 'authentication_completed',
    auth: {
      method: 'oauth_google',  // Or github/microsoft
      user_id: parseJWT(sessionToken).userId,
      tier: tier,
      session_token: sessionToken
    }
  });

  // Update UI
  updateTierBadge(tier);  // "👤 Member" → "🌟 Pro"
  showSuccessToast('✅ Google account linked! You can now sign in on any device.');

  // Clear URL parameters (clean up)
  window.history.replaceState({}, document.title, '/chatkit');
}
```

---

## Security Requirements

### PKCE (Proof Key for Code Exchange)

**Purpose**: Prevent authorization code interception attacks (especially for SPAs)

**Implementation** (Better-Auth handles automatically):

- [ ] Generate code_verifier (random 43-128 char string)
- [ ] Generate code_challenge = SHA256(code_verifier)
- [ ] Send code_challenge in OAuth authorization request
- [ ] Send code_verifier in token exchange request
- [ ] OAuth provider verifies SHA256(code_verifier) == code_challenge

**Note**: PKCE is REQUIRED for public clients (browser-based SPAs) per OAuth 2.1 spec.

---

### State Parameter (CSRF Protection)

**Purpose**: Prevent Cross-Site Request Forgery (CSRF) attacks

**Implementation**:

- [ ] Generate random `state` parameter before OAuth redirect
- [ ] Store state in session or LocalStorage (with timestamp)
- [ ] Verify received state matches stored state on callback
- [ ] Reject OAuth callback if state mismatch (security violation)

**Design-Level State Verification**:
```typescript
function verifyOAuthState(receivedState: string): boolean {
  const storedState = localStorage.getItem('oauth_state');
  const storedTimestamp = localStorage.getItem('oauth_state_timestamp');

  // Check state matches
  if (receivedState !== storedState) {
    console.error('CSRF detected: State mismatch');
    return false;
  }

  // Check state not expired (5 min TTL)
  if (Date.now() - parseInt(storedTimestamp) > 5 * 60 * 1000) {
    console.error('State expired (>5 min)');
    return false;
  }

  return true;
}
```

---

### HTTPS Requirement

**Purpose**: Prevent man-in-the-middle attacks on OAuth flow

**Requirements**:
- [ ] Widget MUST be served over HTTPS in production (not HTTP)
- [ ] OAuth redirect URIs MUST use HTTPS (Google/GitHub/Microsoft reject HTTP)
- [ ] Session cookies MUST have `Secure` flag (HTTPS-only)

**Exception**: `localhost` allowed for local development (OAuth providers allow `http://localhost` for testing)

---

### Token Storage

**Purpose**: Secure storage of OAuth session tokens

**Best Practices**:
- [ ] Store session_token in `httpOnly` cookie (server-side) for maximum security
- [ ] Alternative: LocalStorage (client-side) with XSS protection (Content Security Policy)
- [ ] NEVER store session_token in URL parameters (risk of leakage via browser history)
- [ ] Set session cookie `SameSite=Lax` (CSRF protection)

**Design-Level Cookie Configuration**:
```typescript
// Server-side cookie configuration
res.cookie('session_token', jwt, {
  httpOnly: true,  // Prevents JavaScript access (XSS protection)
  secure: true,     // HTTPS only
  sameSite: 'lax',  // CSRF protection
  maxAge: 30 * 24 * 60 * 60 * 1000  // 30 days
});
```

---

## Error Handling

### Error 1: OAuth Provider Denial (User Clicks "Cancel")

**Scenario**: User clicks "Cancel" in OAuth consent screen

**Callback URL**:
```
GET /chatkit?error=access_denied&error_description=User+denied+access
```

**Widget Behavior**:
- [ ] Parse `error` parameter from URL
- [ ] Display friendly message: "⚠ Google sign-in cancelled. You can try again or use email signup."
- [ ] Return to signup modal (show email/password option)
- [ ] Do NOT upgrade tier (remains at Tier 1)

---

### Error 2: Invalid Authorization Code

**Scenario**: Authorization code expired or already used

**Server Response**:
```json
{
  "error": "invalid_grant",
  "error_description": "Authorization code expired"
}
```

**Widget Behavior**:
- [ ] Display error: "⚠ Sign-in timed out. Please try again."
- [ ] Retry OAuth flow (redirect to OAuth provider again)
- [ ] Log error for monitoring

---

### Error 3: OAuth Provider API Failure (500 Error)

**Scenario**: Google/GitHub/Microsoft API down or slow

**Server Behavior**:
- [ ] Retry token exchange with exponential backoff (3 attempts, 1s, 2s, 4s delays)
- [ ] If all retries fail: Return error to widget

**Widget Behavior**:
- [ ] Display error: "⚠ Unable to connect to Google. Please try again later."
- [ ] Provide fallback: "Use email signup instead"

---

### Error 4: Email Already Linked to Another OAuth Provider

**Scenario**: User tries to link Google account, but email already linked to GitHub account

**Server Behavior**:
- [ ] Detect email conflict in database
- [ ] Return error: "Email already linked to GitHub account"

**Widget Behavior**:
- [ ] Display error: "⚠ This email is already linked to your GitHub account. Sign in with GitHub instead."
- [ ] Offer alternative: "Sign out and create a new account"

---

## Testing Checklist

### OAuth Provider Configuration

- [ ] **Test 1**: Google OAuth consent screen displays correct app name and scopes
- [ ] **Test 2**: GitHub OAuth consent screen displays correct app name and callback URL
- [ ] **Test 3**: Microsoft OAuth consent screen displays correct app name and permissions

### OAuth Flow (Happy Path)

- [ ] **Test 4**: Click "Sign in with Google" → Verify redirect to Google consent screen
- [ ] **Test 5**: Approve Google consent → Verify redirect to widget with session_token
- [ ] **Test 6**: Widget receives session_token → Verify tier badge updates to "🌟 Pro"
- [ ] **Test 7**: Tier 1 user links Google account → Verify tier upgrades to 2
- [ ] **Test 8**: Log out, sign in again with Google → Verify conversation history synced

### OAuth Flow (Error Paths)

- [ ] **Test 9**: Click "Cancel" in OAuth consent → Verify error message displayed
- [ ] **Test 10**: Authorization code expires → Verify retry logic or error message
- [ ] **Test 11**: Google API timeout → Verify fallback to email signup
- [ ] **Test 12**: Email already linked to GitHub → Verify conflict error displayed

### Security

- [ ] **Test 13**: Modify `state` parameter in callback URL → Verify CSRF rejection
- [ ] **Test 14**: Replay authorization code → Verify "invalid_grant" error
- [ ] **Test 15**: Attempt OAuth over HTTP (not HTTPS) → Verify blocked by provider
- [ ] **Test 16**: Session cookie has `httpOnly`, `secure`, `sameSite=lax` flags ✅

### Multi-Provider

- [ ] **Test 17**: Link Google account → Link GitHub account → Verify both providers saved
- [ ] **Test 18**: Sign in with Google on Device A, GitHub on Device B → Verify same user account
- [ ] **Test 19**: Unlink OAuth provider → Verify user can still sign in with email/password

---

## Performance Targets

| Metric | Target | Source |
|--------|--------|--------|
| OAuth redirect latency | ≤2s | Better-Auth integration |
| Token exchange latency | ≤500ms (p95) | OAuth provider API |
| Widget callback handling | ≤100ms | NFR-002 |
| Tier badge update | ≤50ms | NFR-002 |

---

## Privacy & Compliance

### GDPR (General Data Protection Regulation)

- [ ] **Article 6 (Lawful Basis)**: OAuth consent screen = explicit consent for data processing ✅
- [ ] **Article 13 (Transparency)**: Display privacy policy link in OAuth consent screen ✅
- [ ] **Article 17 (Right to Erasure)**: "Unlink OAuth Account" button in Settings ✅

### CCPA (California Consumer Privacy Act)

- [ ] **Do Not Sell**: OAuth data (email, name) MUST NOT be shared with third parties ✅ NFR-013
- [ ] **Data Minimization**: Request minimum OAuth scopes (`openid`, `email`, `profile` only) ✅

### FERPA (Family Educational Rights and Privacy Act)

- [ ] **Age Gate**: OAuth users <13 blocked (COPPA compliance) ✅
- [ ] **Parental Consent**: OAuth users 13-17 require parental consent ✅

---

## Implementation Notes

### OAuth Provider Comparison

| Provider | Pros | Cons | Recommended For |
|----------|------|------|-----------------|
| **Google** | Widest adoption (2B+ users), fast API | Privacy concerns (data collection) | General audience |
| **GitHub** | Developer-friendly, no personal data collection | Limited to developers/tech users | Technical documentation sites |
| **Microsoft** | Enterprise integration (Azure AD), Outlook users | Complex setup (Azure Portal) | Enterprise/educational institutions |

---

### Better-Auth Alternatives

If Better-Auth is not suitable, consider:

1. **NextAuth.js** (for Next.js projects):
   - Pros: Built-in OAuth providers, session management
   - Cons: Tied to Next.js framework

2. **Passport.js** (for Node.js/Express projects):
   - Pros: 500+ authentication strategies, mature ecosystem
   - Cons: Callback-heavy API, requires manual session management

3. **Supabase Auth** (for Supabase projects):
   - Pros: Built-in OAuth, magic links, row-level security
   - Cons: Vendor lock-in to Supabase

**Recommendation**: Better-Auth for framework-agnostic, TypeScript-first authentication

---

## References

- **Pattern 3 (Session Continuity)**: `.claude/skills/chatkit-widget/patterns.md` lines 267-416
- **Tier Upgrade Guide**: `specs/003-chatkit-widget/integration/tier-upgrades.md`
- **authentication_completed Event Schema**: `.claude/skills/chatkit-widget/SKILL.md` lines 190-202
- **FR-015**: OAuth authentication requirement (spec.md line 291)
- **NFR-013**: No third-party data sharing (spec.md line 346)
- **Better-Auth Documentation**: https://better-auth.dev (Phase 7+ reference)

---

**Status**: Design Checklist Complete ✅
**Next Step**: Implement OAuth integration with Better-Auth (Phase 7+)
