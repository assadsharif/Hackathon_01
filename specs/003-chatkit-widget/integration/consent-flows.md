# Privacy Consent Flows Guide

**Document Type**: Integration Guide
**User Story**: US3 (Progressive Signup)
**Phase**: 6 (Design Specification)
**Created**: 2025-12-26

---

## Overview

This guide documents privacy consent workflows required for GDPR, CCPA, FERPA, and COPPA compliance in the ChatKit widget.

**Requirements**:
- FR-018: Widget MUST NOT collect personal data for anonymous users (Tier 0)
- FR-019: Widget MUST display cookie consent banner on first visit (GDPR compliance)
- FR-020: Widget MUST provide "Export Data" button for authenticated users (GDPR Article 20)
- FR-021: Widget MUST provide "Delete Account" button with 30-day retention policy (GDPR Article 17)
- NFR-013: Widget MUST NOT share data with third parties
- NFR-014: Anonymous sessions MUST stay browser-local (no server upload)

**Privacy Regulations**:
1. **GDPR** (EU): General Data Protection Regulation
2. **CCPA** (California, USA): California Consumer Privacy Act
3. **FERPA** (USA): Family Educational Rights and Privacy Act
4. **COPPA** (USA): Children's Online Privacy Protection Act

---

## Consent Modal Taxonomy

**Four Types of Consent Modals**:

| Modal Type | Trigger | Regulation | Required? | User Action |
|------------|---------|------------|-----------|-------------|
| **Cookie Consent Banner** | First visit to site | GDPR Article 7 | ✅ Yes (EU users) | Accept/Reject cookies |
| **Session Upload Consent** | Tier 0 → Tier 1 upgrade | GDPR Article 6 | ✅ Yes (before server upload) | Grant/Deny upload |
| **Age Gate** | Widget load (if user <13) | COPPA, FERPA | ✅ Yes (US users) | Enter birthdate, parental consent |
| **Do Not Sell Opt-Out** | Settings → Privacy | CCPA | ⚠️ Optional (informational) | No data selling occurs |

---

## 1. Cookie Consent Banner (GDPR Article 7)

### Purpose

**Legal Requirement**: GDPR Article 7 - Conditions for consent

**Scope**: EU users only (geolocation-based display)

**Data Collected**:
- Essential cookies: `session_id`, `user_preferences` (theme, language)
- Analytics cookies: None (FR-039: No analytics for anonymous users)
- Third-party cookies: None (NFR-013: No third-party data sharing)

---

### Cookie Consent Banner UI

**Banner Design** (appears at bottom of page on first visit):

```
┌────────────────────────────────────────────────────────────────────┐
│  🍪 We use cookies to save your conversation and preferences.     │
│  No analytics or third-party trackers. Learn more in our          │
│  [Privacy Policy].                                                 │
│                                                                    │
│  [Accept All]  [Reject Non-Essential]  [Customize]                │
└────────────────────────────────────────────────────────────────────┘
```

**Cookie Categories**:

1. **Essential Cookies** (cannot be rejected):
   - `chatkit_session_id` (30-day expiry)
   - `chatkit_preferences` (theme, language)
   - **Purpose**: Core widget functionality (conversation history, user settings)

2. **Non-Essential Cookies** (can be rejected):
   - None (ChatKit widget has no analytics or tracking cookies)

**User Actions**:

- **Accept All** → Set all cookies (essential only, since no non-essential cookies exist)
- **Reject Non-Essential** → Set essential cookies only (same as "Accept All" for ChatKit)
- **Customize** → Show detailed cookie preferences modal (Phase 7+ enhancement)

---

### Cookie Consent State Management

**Design-Level Logic**:

```typescript
function showCookieConsentBanner(): boolean {
  // Check if user already consented
  const cookieConsent = localStorage.getItem('chatkit_cookie_consent');
  if (cookieConsent) {
    return false;  // Already consented, don't show banner
  }

  // Check if user is in EU (geolocation-based)
  const userCountry = getUserCountry();  // IP geolocation
  if (!isEUCountry(userCountry)) {
    // Non-EU users: Auto-consent (GDPR doesn't apply)
    localStorage.setItem('chatkit_cookie_consent', 'auto');
    return false;
  }

  return true;  // EU user, no consent yet → show banner
}

function handleCookieConsent(action: 'accept' | 'reject') {
  if (action === 'accept') {
    // Set essential cookies
    localStorage.setItem('chatkit_cookie_consent', 'granted');
    initializeWidget();  // Enable widget functionality
  } else if (action === 'reject') {
    // Still set essential cookies (required for widget functionality)
    localStorage.setItem('chatkit_cookie_consent', 'essential_only');
    initializeWidget();
  }

  hideCookieBanner();
}
```

**Storage**:
- `chatkit_cookie_consent`: "granted" | "essential_only" | "auto"
- Expiry: 365 days (consent valid for 1 year, then re-prompt)

---

## 2. Session Upload Consent (GDPR Article 6)

### Purpose

**Legal Requirement**: GDPR Article 6 - Lawful basis for processing

**Scope**: All users upgrading from Tier 0 (anonymous) to Tier 1 (authenticated)

**Data Uploaded**:
- Conversation history (user questions + agent responses)
- Bookmarks (content IDs + timestamps)
- Preferences (theme, language)

**Why Consent Required**: Uploading conversation history to server = personal data processing

---

### Session Upload Consent Modal UI

**Modal Design** (appears after user completes email/OAuth signup):

```
┌────────────────────────────────────────────────────────────────┐
│  🔒 Save Your Conversation?                                    │
│                                                                │
│  We'll securely store your 15 messages on our servers so you  │
│  can access them from any device.                             │
│                                                                │
│  ✓ End-to-end encrypted (AES-256)                             │
│  ✓ You can export or delete anytime                           │
│  ✓ We never share data with 3rd parties                       │
│                                                                │
│  [Privacy Policy]  [Cookie Policy]                            │
│                                                                │
│  [Yes, Save My Conversation]  [No, Keep It Local Only]        │
└────────────────────────────────────────────────────────────────┘
```

**User Actions**:

1. **"Yes, Save My Conversation"** (`consent_granted` event):
   - Widget uploads session to `/api/v1/session/merge`
   - Server stores conversation history, bookmarks, preferences
   - User can access data from any device (cross-device sync)

2. **"No, Keep It Local Only"** (`consent_denied` event):
   - Session stays in browser LocalStorage
   - User account created (Tier 1) but empty on server
   - User can access conversation on current device only
   - User can grant consent later via Settings → "Sync Conversation to Server"

---

### Session Upload Consent Flow

**Step-by-Step Flow**:

```
1. User completes email/OAuth signup
   ↓
2. Widget emits authentication_completed event
   ↓
3. Widget displays session upload consent modal
   ↓
4a. If "Yes, Save My Conversation":
   - Widget reads browser-local session (LocalStorage)
   - Widget uploads to POST /api/v1/session/merge
   - Server stores data, returns merged session
   - Widget clears browser-local session (data now on server)
   - Widget displays success toast: "✅ Conversation saved!"
   ↓
4b. If "No, Keep It Local Only":
   - Widget keeps session in LocalStorage
   - Widget records consent_denied in user profile
   - Widget displays toast: "ℹ️ Conversation stays on this device."
   - Widget hides modal
```

**Design-Level Consent Handling**:

```typescript
async function handleSessionUploadConsent(action: 'grant' | 'deny', userId: string) {
  if (action === 'grant') {
    // Upload session to server
    const localSession = readLocalSession();
    const response = await fetch('/api/v1/session/merge', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${sessionToken}` },
      body: JSON.stringify({
        user_id: userId,
        data: localSession,
        consent: 'granted',
        consent_timestamp: new Date().toISOString()
      })
    });

    if (response.ok) {
      clearLocalSession();
      showSuccessToast('✅ Conversation saved!');
    }
  } else if (action === 'deny') {
    // Keep session browser-local
    await fetch('/api/v1/users/{userId}/consent', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${sessionToken}` },
      body: JSON.stringify({
        session_upload_consent: 'denied',
        consent_timestamp: new Date().toISOString()
      })
    });

    showInfoToast('ℹ️ Conversation stays on this device.');
  }

  hideConsentModal();
}
```

---

### Consent Withdrawal (GDPR Article 7.3)

**Legal Requirement**: Users can withdraw consent at any time

**UI Location**: Settings → Privacy → "Manage Data Sync"

**Consent Withdrawal Flow**:

```
1. User navigates to Settings → Privacy
   ↓
2. Widget displays current consent status:
   - ✅ "Conversation synced to server (granted 2025-12-26)"
   - [Withdraw Consent & Delete Server Data]
   ↓
3. User clicks "Withdraw Consent"
   ↓
4. Widget displays confirmation modal:
   "⚠ This will delete all your server-stored conversations and keep data browser-local only. Continue?"
   [Cancel] [Delete Server Data]
   ↓
5. If confirmed:
   - Widget sends DELETE /api/v1/users/{userId}/session
   - Server deletes all conversation history, bookmarks
   - Widget downloads session data to browser (before deletion)
   - Widget displays success: "✅ Server data deleted. Conversation now browser-local only."
```

---

## 3. Age Gate (COPPA, FERPA)

### Purpose

**Legal Requirement**: COPPA (Children's Online Privacy Protection Act) - Users <13 cannot create accounts without parental consent

**Scope**: US users only (geolocation-based display)

**Age Thresholds**:
- **<13 years**: Blocked (cannot create account, COPPA compliance)
- **13-17 years**: Parental consent required (FERPA compliance)
- **18+ years**: No restrictions

---

### Age Gate UI (First-Time Signup)

**Age Gate Modal** (appears before signup modal):

```
┌────────────────────────────────────────────────────────────────┐
│  🎂 How old are you?                                           │
│                                                                │
│  We need to verify your age to comply with privacy laws.      │
│                                                                │
│  Birthdate: [MM] / [DD] / [YYYY]                              │
│                                                                │
│  [Continue]  [Cancel]                                          │
└────────────────────────────────────────────────────────────────┘
```

**User Actions**:

1. **User <13 years**:
   - Widget displays: "⚠ You must be at least 13 years old to create an account."
   - Widget blocks signup (no account creation)
   - User can still use widget anonymously (Tier 0)

2. **User 13-17 years**:
   - Widget displays parental consent modal (see below)
   - Signup blocked until parent approves

3. **User 18+ years**:
   - Widget proceeds to normal signup modal (email/OAuth)

---

### Parental Consent Modal (FERPA Requirement)

**Modal Design** (for users 13-17 years):

```
┌────────────────────────────────────────────────────────────────┐
│  👨‍👩‍👧 Parental Consent Required                                   │
│                                                                │
│  You're under 18, so we need your parent/guardian's           │
│  permission to create an account.                             │
│                                                                │
│  Parent's Email: _______________________________              │
│                                                                │
│  We'll send a consent form to this email.                     │
│                                                                │
│  [Send Consent Request]  [Cancel]                             │
└────────────────────────────────────────────────────────────────┘
```

**Parental Consent Flow**:

```
1. User enters parent's email
   ↓
2. Widget sends POST /api/v1/auth/parental-consent-request
   {
     "child_email": "student@email.com",
     "parent_email": "parent@email.com",
     "child_age": 15
   }
   ↓
3. Server sends email to parent with consent link:
   "Subject: Parental Consent Required for Physical AI Book"
   "Your child (student@email.com) wants to create an account. Click here to approve: [Approve Link]"
   ↓
4. Parent clicks [Approve Link] → Redirects to consent form
   ↓
5. Parent fills consent form:
   - "I give permission for my child to create an account."
   - "I understand data collected: conversation history, bookmarks, preferences."
   - [Approve] [Deny]
   ↓
6. If approved:
   - Server creates user account (status: "pending_email_verification")
   - Server sends email to child: "Your parent approved! Please verify your email to activate your account."
   ↓
7. Child verifies email → Account activated (Tier 1)
```

---

## 4. Data Export (GDPR Article 20)

### Purpose

**Legal Requirement**: GDPR Article 20 - Right to data portability

**Scope**: All authenticated users (Tier 1+)

**Exported Data**:
- Conversation history (all messages, timestamps, citations)
- Bookmarks (content IDs, timestamps)
- Preferences (theme, language)
- Account metadata (user ID, tier, OAuth providers)

**Export Formats**:
- **JSON**: Machine-readable format (for migration to other platforms)
- **Markdown**: Human-readable format (for archival)

---

### Data Export UI

**UI Location**: Settings → Privacy → "Export My Data"

**Export Button**:
```
Settings > Privacy
┌────────────────────────────────────────────────────────────────┐
│  📥 Export My Data (GDPR Article 20)                           │
│                                                                │
│  Download a copy of all your conversations, bookmarks, and    │
│  preferences.                                                  │
│                                                                │
│  Format: [JSON ▼] [Markdown]                                  │
│                                                                │
│  [Download Data]                                               │
└────────────────────────────────────────────────────────────────┘
```

**Export Flow**:

```
1. User clicks "Download Data"
   ↓
2. Widget sends GET /api/v1/users/{userId}/export?format=json
   ↓
3. Server generates export file:
   - Fetches all user data from database
   - Formats as JSON or Markdown
   - Returns file download
   ↓
4. Widget triggers browser download:
   - Filename: "chatkit-export-2025-12-26.json"
   - Size: ~500 KB for 100 messages
   ↓
5. Widget displays success toast: "✅ Data exported successfully!"
```

---

### Export File Format (JSON)

**JSON Export Schema**:

```json
{
  "export_version": "1.0",
  "export_date": "2025-12-26T10:00:00.000Z",
  "user": {
    "user_id": "user-uuid",
    "email": "user@example.com",
    "tier": "lightweight",
    "created_at": "2025-12-01T10:00:00.000Z"
  },
  "conversation_history": [
    {
      "id": "msg-uuid-1",
      "role": "user",
      "content": "What is embodied intelligence?",
      "timestamp": "2025-12-26T10:15:00.000Z"
    },
    {
      "id": "msg-uuid-2",
      "role": "agent",
      "content": "Embodied intelligence refers to...",
      "timestamp": "2025-12-26T10:15:02.500Z",
      "citations": [
        {
          "id": "citation-1",
          "url": "/docs/module-2-embodied/embodied-intelligence#definition"
        }
      ]
    }
  ],
  "bookmarks": [
    {
      "content_id": "module-2-embodied/embodied-intelligence",
      "timestamp": "2025-12-26T10:20:00.000Z"
    }
  ],
  "preferences": {
    "theme": "dark",
    "language": "en"
  }
}
```

---

### Export File Format (Markdown)

**Markdown Export Schema**:

```markdown
# ChatKit Conversation Export

**Export Date**: 2025-12-26
**User**: user@example.com
**Tier**: Lightweight

---

## Conversation History

### 2025-12-26 10:15:00
**You**: What is embodied intelligence?

**ChatKit**: Embodied intelligence refers to the theory that intelligence emerges from the interaction between an agent's body, environment, and sensorimotor experiences.

*Sources*:
- [Module 2: Embodied Intelligence > Definition](/docs/module-2-embodied/embodied-intelligence#definition)

---

## Bookmarks

- Module 2: Embodied Intelligence (bookmarked on 2025-12-26 10:20:00)

---

## Preferences

- Theme: Dark
- Language: English
```

---

## 5. Data Deletion (GDPR Article 17)

### Purpose

**Legal Requirement**: GDPR Article 17 - Right to erasure ("right to be forgotten")

**Scope**: All authenticated users (Tier 1+)

**Deleted Data**:
- User account (email, OAuth providers)
- Conversation history (all messages, citations)
- Bookmarks (all saved content)
- Preferences (theme, language)
- Session tokens (logout all devices)

**Retention Policy**: 30-day soft delete (FR-021)

---

### Data Deletion UI

**UI Location**: Settings → Account → "Delete Account"

**Delete Account Button**:
```
Settings > Account
┌────────────────────────────────────────────────────────────────┐
│  ⚠️ Danger Zone                                                │
│                                                                │
│  🗑️ Delete Account (GDPR Article 17)                           │
│                                                                │
│  Permanently delete your account and all associated data.     │
│  This action cannot be undone after 30 days.                  │
│                                                                │
│  [Delete My Account]                                           │
└────────────────────────────────────────────────────────────────┘
```

**Delete Account Flow**:

```
1. User clicks "Delete My Account"
   ↓
2. Widget displays confirmation modal:
   "⚠ Are you sure you want to delete your account?"
   "Your 15 conversations and 3 bookmarks will be permanently deleted after 30 days."
   [Cancel] [Yes, Delete My Account]
   ↓
3. User confirms deletion
   ↓
4. Widget sends DELETE /api/v1/users/{userId}
   ↓
5. Server soft-deletes account:
   - Sets user.status = "deleted"
   - Sets user.deletion_date = now() + 30 days
   - Revokes all session tokens (logout all devices)
   - Sends confirmation email: "Account deletion scheduled for 2026-01-25"
   ↓
6. Widget logs out user and displays:
   "✅ Account deletion scheduled. You have 30 days to cancel by logging in again."
```

---

### Soft Delete vs. Hard Delete

**30-Day Soft Delete Period** (FR-021):

- **Days 0-30**: Account marked as "deleted" but data retained
  - User can log in to cancel deletion
  - Data not accessible via widget (appears deleted to user)
  - Server keeps data for recovery

- **Day 30+**: Permanent hard delete
  - Server permanently deletes all user data from database
  - Deletion cannot be reversed
  - User receives final email: "Your account has been permanently deleted."

**Design-Level Soft Delete Logic**:

```typescript
// Server-side soft delete
async function softDeleteUser(userId: string) {
  const deletionDate = new Date();
  deletionDate.setDate(deletionDate.getDate() + 30);  // 30 days from now

  await db.users.update({
    where: { id: userId },
    data: {
      status: 'deleted',
      deletion_date: deletionDate
    }
  });

  // Revoke all session tokens
  await db.sessions.deleteMany({ where: { user_id: userId } });

  // Send confirmation email
  await sendEmail({
    to: user.email,
    subject: 'Account Deletion Scheduled',
    body: `Your account will be permanently deleted on ${deletionDate.toDateString()}. Log in to cancel.`
  });
}

// Cron job: Run daily to hard-delete accounts past 30 days
async function hardDeleteExpiredAccounts() {
  const expiredUsers = await db.users.findMany({
    where: {
      status: 'deleted',
      deletion_date: { lte: new Date() }  // Deletion date passed
    }
  });

  for (const user of expiredUsers) {
    // Permanently delete all user data
    await db.conversations.deleteMany({ where: { user_id: user.id } });
    await db.bookmarks.deleteMany({ where: { user_id: user.id } });
    await db.users.delete({ where: { id: user.id } });

    console.log(`Hard-deleted user ${user.id}`);
  }
}
```

---

## 6. CCPA "Do Not Sell" Opt-Out

### Purpose

**Legal Requirement**: CCPA Section 1798.120 - Right to opt-out of sale of personal information

**Scope**: California residents (US users)

**ChatKit Widget Status**: No data selling occurs (NFR-013)

**UI Purpose**: Informational only (show compliance, build trust)

---

### "Do Not Sell" UI

**UI Location**: Settings → Privacy → "Do Not Sell My Data"

**CCPA Opt-Out Section**:
```
Settings > Privacy
┌────────────────────────────────────────────────────────────────┐
│  🛡️ Do Not Sell My Data (CCPA)                                 │
│                                                                │
│  We do NOT sell your personal data to third parties.          │
│                                                                │
│  Status: ✅ Data selling disabled (always)                     │
│                                                                │
│  Learn more: [Privacy Policy]                                 │
└────────────────────────────────────────────────────────────────┘
```

**No Action Required**: Widget displays informational message only (no toggle needed, since data selling never occurs)

---

## Testing Checklist

### Cookie Consent

- [ ] **Test 1**: First visit → Verify cookie consent banner appears (EU users only)
- [ ] **Test 2**: Click "Accept All" → Verify banner disappears, cookies set
- [ ] **Test 3**: Reject cookies → Verify essential cookies still set (widget works)
- [ ] **Test 4**: Consent expires (365 days) → Verify banner re-appears

### Session Upload Consent

- [ ] **Test 5**: Complete signup → Verify session upload consent modal appears
- [ ] **Test 6**: Grant consent → Verify conversation uploaded to server
- [ ] **Test 7**: Deny consent → Verify conversation stays browser-local
- [ ] **Test 8**: Withdraw consent → Verify server data deleted

### Age Gate

- [ ] **Test 9**: Enter birthdate <13 years → Verify signup blocked
- [ ] **Test 10**: Enter birthdate 13-17 years → Verify parental consent modal appears
- [ ] **Test 11**: Enter birthdate 18+ years → Verify normal signup proceeds
- [ ] **Test 12**: Parent approves consent → Verify child account activated

### Data Export

- [ ] **Test 13**: Click "Export Data" (JSON) → Verify download starts
- [ ] **Test 14**: Verify JSON export contains all conversations, bookmarks, preferences
- [ ] **Test 15**: Click "Export Data" (Markdown) → Verify human-readable format
- [ ] **Test 16**: Export file size <10 MB for 1000 messages

### Data Deletion

- [ ] **Test 17**: Click "Delete Account" → Verify confirmation modal appears
- [ ] **Test 18**: Confirm deletion → Verify account soft-deleted (30-day retention)
- [ ] **Test 19**: Log in during 30-day window → Verify account restored
- [ ] **Test 20**: After 30 days → Verify account hard-deleted (cannot log in)

---

## Privacy Compliance Matrix

| Regulation | Article | Requirement | Widget Implementation | Status |
|------------|---------|-------------|----------------------|--------|
| **GDPR** | Art. 6 | Lawful basis for processing | Session upload consent modal | ✅ FR-019 |
| **GDPR** | Art. 7 | Conditions for consent | Cookie consent banner (EU only) | ✅ FR-019 |
| **GDPR** | Art. 13 | Information to be provided | Privacy policy link in modals | ✅ |
| **GDPR** | Art. 17 | Right to erasure | "Delete Account" button (30-day retention) | ✅ FR-021 |
| **GDPR** | Art. 20 | Right to data portability | "Export Data" button (JSON/Markdown) | ✅ FR-020 |
| **CCPA** | §1798.120 | Right to opt-out of sale | "Do Not Sell" (informational) | ✅ NFR-013 |
| **COPPA** | §312.3 | Parental consent | Age gate (<13 blocked, 13-17 parental consent) | ✅ |
| **FERPA** | §99.3 | Parental consent (education) | Parental consent for 13-17 years | ✅ |

---

## References

- **Pattern 3 (Session Continuity)**: `.claude/skills/chatkit-widget/patterns.md` lines 372-388
- **Tier Upgrade Guide**: `specs/003-chatkit-widget/integration/tier-upgrades.md` lines 182-239 (Privacy consent modal)
- **FR-018 to FR-021**: Privacy compliance requirements (spec.md lines 297-301)
- **NFR-013, NFR-014**: Data handling requirements (spec.md lines 346-347)
- **GDPR Official Text**: https://gdpr-info.eu
- **CCPA Official Text**: https://oag.ca.gov/privacy/ccpa

---

**Status**: Design Guide Complete ✅
**Next Step**: Implement privacy consent flows (Phase 7+)
