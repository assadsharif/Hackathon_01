# Tier Upgrade Guide: Progressive Signup with Session Continuity

**Document Type**: Integration Guide
**User Story**: US3 (Progressive Signup)
**Phase**: 6 (Design Specification)
**Created**: 2025-12-26

---

## Overview

This guide documents how users upgrade through 4 authentication tiers while preserving conversation history, bookmarks, and preferences across devices.

**Tier Progression**:
```
Tier 0 (Anonymous) → Tier 1 (Lightweight) → Tier 2 (Full Profile) → Tier 3 (Premium)
```

**Design Pattern**: Pattern 3 (Session Continuity with Tier Upgrades)

---

## Tier Definitions

| Tier | Name | Authentication | Key Features | Data Storage | Upgrade Trigger |
|------|------|----------------|--------------|--------------|-----------------|
| **0** | Anonymous Learner | None | Q&A, browser-local sessions (30 days) | LocalStorage only | "Save Progress" button after 10 messages |
| **1** | Lightweight Signup | Email + Password | Bookmarks, export history, server-sync | Server + LocalStorage | "Sign in with Google" button |
| **2** | Full Profile | OAuth (Google, GitHub, Microsoft) | Cross-device sync, learning paths, progress tracking | Server only | "Upgrade to Premium" button |
| **3** | Premium (Instructor) | OAuth + Subscription | Analytics dashboards, student engagement tracking | Server + Analytics DB | Subscription purchase |

---

## Tier 0 → Tier 1: Anonymous to Lightweight Signup

### Trigger Scenarios

**Scenario 1: "Save Progress" Button (FR-013)**

**Condition**: User asks 10+ questions in current session

**UI Behavior**:
1. Widget displays "Save Progress" button in chat header (non-intrusive)
2. Button text: "💾 Save your conversation (30 seconds)"
3. Button appears after 10th user message (message counter in session metadata)

**Design-Level Logic**:
```typescript
function checkSaveProgressPrompt(session: Session): boolean {
  const messageCount = session.conversation_history.filter(m => m.role === "user").length;
  return messageCount >= 10 && session.tier === "anonymous";
}
```

---

**Scenario 2: Bookmark Feature Access**

**Condition**: Anonymous user tries to bookmark content

**UI Behavior**:
1. User clicks bookmark button on a message or documentation section
2. Tooltip appears: "Sign up to save bookmarks across devices"
3. Click tooltip → Opens signup modal

**Event Flow**:
```
User clicks bookmark → signup_initiated (trigger: "bookmark_feature_access") → Signup modal opens
```

---

**Scenario 3: Rate Limiting (FR-013)**

**Condition**: Anonymous user exceeds rate limit (10 questions in 10 minutes)

**UI Behavior**:
1. Widget displays rate limit message: "You're asking great questions! Create a free account for unlimited access."
2. Message includes "Sign Up" button
3. Clicking button → Opens signup modal

**Event Payload**:
```json
{
  "event": "signup_initiated",
  "flow": {
    "type": "progressive_signup",
    "current_tier": "anonymous",
    "target_tier": "lightweight",
    "trigger": "rate_limit_reached",
    "context": {
      "current_conversation_length": 15,
      "rate_limit_exceeded_by": 5
    }
  }
}
```

---

### Signup Modal UI (Tier 0 → 1)

**Modal Design**:
```
┌────────────────────────────────────────┐
│  💾 Save Your Conversation             │
│                                        │
│  Continue learning across devices.     │
│  Your 15 messages will be securely     │
│  saved to your account.                │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Email: ______________________    │ │
│  │ Password: ____________________   │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │   Continue with Google (OAuth)   │ │ ← Optional OAuth shortcut
│  └──────────────────────────────────┘ │
│                                        │
│  [Create Account]  [Maybe Later]      │
└────────────────────────────────────────┘
```

**Accessibility**:
- Modal MUST trap focus (Tab cycles through email, password, buttons)
- Escape key MUST close modal (triggers `signup_cancelled` event)
- Screen reader announcement: "Signup modal opened. 15 messages will be saved to your account."

---

### Session Merge Workflow (Tier 0 → 1)

**Step-by-Step Flow**:

```
1. User clicks "Create Account" in signup modal
   ↓
2. Widget validates email + password (client-side: email format, password ≥8 chars)
   ↓
3. Widget sends POST /api/v1/auth/signup with email + password
   ↓
4. Server creates user account, returns user_id + session_token (JWT)
   ↓
5. Widget emits authentication_completed event
   {
     "event": "authentication_completed",
     "auth": {
       "method": "email_password",
       "user_id": "user-uuid",
       "tier": "lightweight",
       "session_token": "jwt-token"
     }
   }
   ↓
6. Widget displays GDPR consent modal (CRITICAL - see Privacy Consent section below)
   ↓
7. If consent granted:
   - Widget reads browser-local session from LocalStorage
   - Widget uploads session to POST /api/v1/session/merge
   {
     "anonymous_session_id": "anon-uuid",
     "user_id": "user-uuid",
     "data": {
       "conversation_history": [...],
       "bookmarks": [],
       "preferences": {"theme": "dark"}
     }
   }
   ↓
8. Server merges browser-local → server session
   - Deduplicates bookmarks by content_id
   - Sorts conversation_history by timestamp
   - Preserves preferences (server-side wins if conflict)
   ↓
9. Server returns merged session + new session_id
   {
     "session_id": "server-uuid",
     "merged": true,
     "conversation_history": [...],  // 15 messages from browser-local
     "bookmarks": [],
     "preferences": {"theme": "dark"}
   }
   ↓
10. Widget updates UI:
    - Close signup modal
    - Display success toast: "✅ Account created! Your 15 messages are saved."
    - Update chat header with tier badge: "👤 Member"
    - Clear browser-local session (data now on server)
   ↓
11. Widget stores session_token in LocalStorage for future sessions
```

**Design-Level Session Merge Code**:
```typescript
async function mergeAnonymousSession(anonymousSessionId: string, userId: string) {
  // Step 6: Read browser-local session
  const localSession = localStorage.getItem('chatkit_history');
  const localBookmarks = localStorage.getItem('chatkit_bookmarks');
  const localPreferences = localStorage.getItem('chatkit_preferences');

  // Step 7: Upload to server
  const response = await fetch('/api/v1/session/merge', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${sessionToken}`
    },
    body: JSON.stringify({
      anonymous_session_id: anonymousSessionId,
      user_id: userId,
      data: {
        conversation_history: JSON.parse(localSession || '[]'),
        bookmarks: JSON.parse(localBookmarks || '[]'),
        preferences: JSON.parse(localPreferences || '{}')
      }
    })
  });

  // Step 9: Update UI with merged session
  const mergedSession = await response.json();
  updateChatHistory(mergedSession.conversation_history);
  updateTierBadge('lightweight');

  // Step 10: Clear browser-local session
  localStorage.removeItem('chatkit_history');
  localStorage.removeItem('chatkit_bookmarks');
  localStorage.setItem('session_token', mergedSession.session_token);
}
```

---

## Privacy Consent Modal (GDPR Requirement)

**CRITICAL**: Explicit consent MUST be obtained before uploading conversation history to server (GDPR Article 6: Lawful Basis for Processing)

**Consent Modal UI**:
```
┌────────────────────────────────────────┐
│  🔒 Save Your Conversation?            │
│                                        │
│  We'll securely store your 15 messages│
│  on our servers so you can access them│
│  from any device.                      │
│                                        │
│  ✓ End-to-end encrypted (AES-256)     │
│  ✓ You can export or delete anytime   │
│  ✓ We never share data with 3rd parties│
│                                        │
│  [Yes, Save My Conversation]           │
│  [No, Keep It Local Only]              │
└────────────────────────────────────────┘
```

**User Actions**:
1. **"Yes, Save My Conversation"** → `consent_granted` event → Session merge proceeds (Step 7-10)
2. **"No, Keep It Local Only"** → `consent_denied` event → Session stays browser-local, account created but empty

**If Consent Denied**:
- User account created successfully (Tier 1)
- Session data stays in browser LocalStorage
- User can access conversation on current device only
- User can grant consent later via Settings → "Sync Conversation to Server"

---

## Tier 1 → Tier 2: Lightweight to Full Profile (OAuth Upgrade)

### Trigger Scenarios

**Scenario 1: Cross-Device Sync Prompt**

**Condition**: User logs in on a second device (different browser or machine)

**UI Behavior**:
1. Widget detects user_id but no conversation history on current device
2. Widget displays prompt: "Sign in with Google to sync your conversations across all devices"
3. Click prompt → Opens OAuth signup modal

---

**Scenario 2: Manual OAuth Upgrade**

**Condition**: User clicks "Sign in with OAuth" in Settings

**UI Behavior**:
1. User navigates to Settings → Account → "Link Google Account"
2. Click button → Opens OAuth consent screen (Google)
3. OAuth completes → Returns to widget with OAuth token

---

### OAuth Signup Flow (Tier 1 → 2)

**Step-by-Step Flow**:

```
1. User clicks "Sign in with Google" button
   ↓
2. Widget redirects to Better-Auth OAuth endpoint
   GET /api/v1/auth/oauth/google?redirect_uri=/chatkit
   ↓
3. Google consent screen appears (user approves permissions)
   ↓
4. Google redirects back to widget with authorization code
   GET /chatkit?code=google-auth-code
   ↓
5. Widget exchanges code for OAuth token
   POST /api/v1/auth/oauth/google/callback
   {
     "code": "google-auth-code",
     "user_id": "existing-user-uuid"  // Link to existing Tier 1 account
   }
   ↓
6. Server links OAuth provider to existing user account
   - Updates user.oauth_providers[] = ["google"]
   - Upgrades user.tier = "full"
   - Returns session_token (JWT with new tier)
   ↓
7. Widget emits authentication_completed event
   {
     "event": "authentication_completed",
     "auth": {
       "method": "oauth_google",
       "user_id": "user-uuid",
       "tier": "full",
       "session_token": "jwt-token-with-tier-2"
     }
   }
   ↓
8. Widget updates UI:
   - Display success toast: "✅ Google account linked! You can now sign in on any device."
   - Update tier badge: "👤 Member → 🌟 Pro"
   - Enable new features: Learning paths, progress tracking
   ↓
9. No session merge needed (user already has server-side session from Tier 1)
```

**Design-Level OAuth Link Code**:
```typescript
async function linkOAuthProvider(provider: 'google' | 'github' | 'microsoft', userId: string) {
  // Step 2: Redirect to OAuth provider
  const redirectUri = `${window.location.origin}/chatkit`;
  window.location.href = `/api/v1/auth/oauth/${provider}?redirect_uri=${redirectUri}&user_id=${userId}`;

  // Step 4-6: Handle OAuth callback (on page load)
  const urlParams = new URLSearchParams(window.location.search);
  const authCode = urlParams.get('code');

  if (authCode) {
    const response = await fetch(`/api/v1/auth/oauth/${provider}/callback`, {
      method: 'POST',
      body: JSON.stringify({ code: authCode, user_id: userId })
    });

    const { session_token, tier } = await response.json();

    // Step 8: Update UI
    localStorage.setItem('session_token', session_token);
    updateTierBadge(tier);
    showSuccessToast(`${provider} account linked!`);
  }
}
```

---

## Tier 2 → Tier 3: Full Profile to Premium (Subscription Upgrade)

### Trigger Scenarios

**Scenario 1: Premium Feature Paywall**

**Condition**: User tries to access instructor analytics dashboard

**UI Behavior**:
1. User clicks "Analytics" tab in widget
2. Widget displays paywall: "Upgrade to Premium to access student engagement analytics"
3. Click "Upgrade" → Redirects to payment page

---

**Scenario 2: Manual Subscription Upgrade**

**Condition**: User navigates to Settings → Subscription → "Upgrade to Premium"

**UI Behavior**:
1. Widget displays pricing modal: "$9.99/month for Premium features"
2. User enters payment details (credit card or PayPal)
3. Payment successful → Tier upgraded to 3

---

### Subscription Upgrade Flow (Tier 2 → 3)

**Step-by-Step Flow**:

```
1. User clicks "Upgrade to Premium" button
   ↓
2. Widget redirects to payment provider (Stripe checkout)
   ↓
3. User completes payment
   ↓
4. Stripe webhook notifies server of successful payment
   POST /api/v1/webhooks/stripe
   {
     "event": "checkout.session.completed",
     "user_id": "user-uuid",
     "subscription_id": "sub-uuid"
   }
   ↓
5. Server upgrades user.tier = "premium"
   - Activates premium features (analytics, custom branding)
   - Returns new session_token (JWT with tier 3)
   ↓
6. Widget polls for tier update (every 2 seconds, max 10 seconds)
   GET /api/v1/users/{user_id}/tier
   ↓
7. Widget receives tier = "premium"
   ↓
8. Widget updates UI:
   - Display success toast: "🎉 Welcome to Premium!"
   - Update tier badge: "🌟 Pro → 💎 Premium"
   - Enable premium features: Analytics dashboard, custom branding
```

**Note**: No session merge needed for Tier 2 → 3 upgrade. This is a feature unlock, not a data migration.

---

## Tier Badges (Visual Indicators)

**Purpose**: Show user's current tier in chat header

**Tier Badge UI**:
```
Chat Header:
┌─────────────────────────────────────┐
│ 💬 ChatKit  [Tier Badge: 👤 Member] │
└─────────────────────────────────────┘
```

**Tier Badge Designs**:

| Tier | Badge Text | Icon | Color |
|------|-----------|------|-------|
| **0 (Anonymous)** | Anonymous | 👻 | Gray (#888) |
| **1 (Lightweight)** | Member | 👤 | Blue (#4A90E2) |
| **2 (Full Profile)** | Pro | 🌟 | Purple (#7B68EE) |
| **3 (Premium)** | Premium | 💎 | Gold (#FFD700) |

**Design-Level Badge Rendering**:
```typescript
function renderTierBadge(tier: Tier): string {
  const badges = {
    anonymous: { icon: '👻', text: 'Anonymous', color: '#888' },
    lightweight: { icon: '👤', text: 'Member', color: '#4A90E2' },
    full: { icon: '🌟', text: 'Pro', color: '#7B68EE' },
    premium: { icon: '💎', text: 'Premium', color: '#FFD700' }
  };

  const badge = badges[tier];
  return `<span class="tier-badge" style="color: ${badge.color}">${badge.icon} ${badge.text}</span>`;
}
```

---

## Session Merge Conflict Resolution

### Scenario: Multi-Device Session Merge

**Problem**: User has browser-local sessions on 2 devices (Device A: 10 messages, Device B: 8 messages) and signs up from Device A

**Solution**: Server merges both sessions chronologically

**Merge Logic**:

```typescript
// Design-level merge logic
function mergeConversationHistories(sessionA: Message[], sessionB: Message[]): Message[] {
  const combined = [...sessionA, ...sessionB];

  // Sort by timestamp (chronological order)
  const sorted = combined.sort((a, b) =>
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  // Deduplicate by message ID (if user asked same question on both devices)
  const deduplicated = deduplicateByMessageId(sorted);

  return deduplicated;
}

function deduplicateBookmarks(bookmarksA: Bookmark[], bookmarksB: Bookmark[]): Bookmark[] {
  const combined = [...bookmarksA, ...bookmarksB];

  // Group by content_id
  const grouped = groupBy(combined, 'content_id');

  // For each content_id, keep earliest bookmark
  const deduplicated = Object.values(grouped).map(group => {
    return group.sort((a, b) =>
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    )[0];
  });

  return deduplicated;
}

function mergePreferences(prefsA: Preferences, prefsB: Preferences): Preferences {
  // Server-side preferences win (most recent)
  return { ...prefsA, ...prefsB };
}
```

---

## Error Handling

### Error 1: Session Merge API Failure

**Scenario**: Network timeout during session merge (Step 7)

**Fallback Behavior**:
1. Widget displays error: "⚠ Unable to sync conversation. Your messages are still saved locally."
2. Widget enables "Retry Sync" button
3. User clicks "Retry" → Resends session merge request with exponential backoff

**Design-Level Retry Logic**:
```typescript
async function retrySessionMerge(anonymousSessionId: string, userId: string, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      await mergeAnonymousSession(anonymousSessionId, userId);
      showSuccessToast('✅ Conversation synced successfully!');
      return;
    } catch (error) {
      if (i === retries - 1) {
        // All retries failed
        showError('Unable to sync conversation. Your messages are saved locally.');
        enableRetryButton();
      } else {
        // Wait before retrying (exponential backoff: 1s, 2s, 4s)
        await sleep(Math.pow(2, i) * 1000);
      }
    }
  }
}
```

---

### Error 2: OAuth Provider Failure

**Scenario**: Google OAuth consent screen returns error (user denies permissions)

**Fallback Behavior**:
1. Widget displays error: "⚠ Google sign-in cancelled. You can try again or use email signup."
2. Widget returns to signup modal with email/password option
3. No tier upgrade occurs (remains at current tier)

---

### Error 3: Payment Failure (Tier 2 → 3)

**Scenario**: Stripe payment declined

**Fallback Behavior**:
1. Widget displays error: "⚠ Payment declined. Please check your payment method."
2. Widget returns to payment modal
3. User can update payment method or cancel upgrade

---

## Testing Checklist

### Tier 0 → 1 Upgrade

- [ ] **Test 1**: Ask 10 questions → Verify "Save Progress" button appears
- [ ] **Test 2**: Click bookmark → Verify signup modal opens
- [ ] **Test 3**: Complete email signup → Verify GDPR consent modal appears
- [ ] **Test 4**: Grant consent → Verify 10 messages merged to server
- [ ] **Test 5**: Deny consent → Verify messages stay browser-local, account created
- [ ] **Test 6**: Session merge fails → Verify retry button appears
- [ ] **Test 7**: Close signup modal → Verify `signup_cancelled` event emitted

### Tier 1 → 2 Upgrade

- [ ] **Test 8**: Click "Sign in with Google" → Verify OAuth consent screen appears
- [ ] **Test 9**: Approve OAuth → Verify tier badge updates to "🌟 Pro"
- [ ] **Test 10**: Deny OAuth permissions → Verify error message, tier stays 1
- [ ] **Test 11**: Link GitHub account (Tier 1 user) → Verify tier upgrades to 2
- [ ] **Test 12**: Log in on Device B with OAuth → Verify conversation history synced

### Tier 2 → 3 Upgrade

- [ ] **Test 13**: Click "Upgrade to Premium" → Verify payment modal appears
- [ ] **Test 14**: Complete payment → Verify tier badge updates to "💎 Premium"
- [ ] **Test 15**: Payment declined → Verify error message, tier stays 2
- [ ] **Test 16**: Premium features enabled → Verify analytics dashboard accessible

### Session Merge Conflicts

- [ ] **Test 17**: Sign up with 10 messages on Device A, 8 messages on Device B → Verify 18 messages merged chronologically
- [ ] **Test 18**: Bookmark same page on 2 devices → Verify deduplicated (1 bookmark, earliest timestamp)
- [ ] **Test 19**: Set theme=dark on Device A, theme=light on Device B → Verify server preference wins

### Accessibility

- [ ] **Test 20**: Signup modal opens → Verify focus trapped (Tab cycles through fields)
- [ ] **Test 21**: Press Escape in modal → Verify modal closes
- [ ] **Test 22**: Screen reader → Verify "Signup modal opened" announcement
- [ ] **Test 23**: High-contrast mode → Verify tier badge visible (≥4.5:1 contrast)

---

## Performance Targets

| Metric | Target | Source |
|--------|--------|--------|
| Signup modal display | ≤100ms | NFR-002 |
| Session merge API response | ≤500ms (p95) | Pattern 3 |
| OAuth redirect latency | ≤2s | Better-Auth integration |
| Tier badge update | ≤50ms | NFR-002 |
| GDPR consent modal display | ≤100ms | Pattern 3 |

---

## Privacy Compliance

### GDPR (General Data Protection Regulation)

- [ ] **Article 6 (Lawful Basis)**: Explicit consent modal before server upload ✅
- [ ] **Article 17 (Right to Erasure)**: "Delete Account" button (30-day retention) ✅ FR-021
- [ ] **Article 20 (Data Portability)**: "Export Data" button (JSON/Markdown) ✅ FR-020
- [ ] **Article 7 (Consent Withdrawal)**: User can withdraw consent via Settings → "Keep Data Local" ✅

### CCPA (California Consumer Privacy Act)

- [ ] **Do Not Sell**: Widget MUST NOT share data with third parties ✅ NFR-013
- [ ] **Opt-Out**: "Do Not Sell My Data" option in Settings ✅

### FERPA (Family Educational Rights and Privacy Act)

- [ ] **Age Gate**: Users <13 cannot create accounts (COPPA compliance) ✅
- [ ] **Parental Consent**: Users 13-17 require parental consent for Tier 1+ ✅

---

## References

- **Pattern 3 (Session Continuity)**: `.claude/skills/chatkit-widget/patterns.md` lines 267-416
- **signup_initiated Event Schema**: `.claude/skills/chatkit-widget/SKILL.md` lines 168-182
- **authentication_completed Event Schema**: `.claude/skills/chatkit-widget/SKILL.md` lines 190-202
- **Better-Auth MCP Server**: `.claude/mcp/better-auth/README.md`
- **FR-012 to FR-017**: Progressive signup requirements (spec.md lines 288-293)
- **NFR-013, NFR-014**: Privacy compliance requirements (spec.md lines 346-347)

---

**Status**: Design Guide Complete ✅
**Next Step**: Implement tier upgrade flows (Phase 7+)
