# Session Persistence Checklist

**Document Type**: Implementation Checklist
**User Story**: US1 (Frictionless Q&A), US3 (Progressive Signup)
**Phase**: 6 (Design Specification)
**Created**: 2025-12-26

---

## Overview

This checklist ensures correct implementation of browser-local session persistence for anonymous users (Tier 0) and server-side session sync for authenticated users (Tier 1+).

**Requirements**:
- FR-005: Widget MUST persist anonymous user sessions in browser localStorage for 30 days
- NFR-014: Widget MUST store anonymous sessions in browser localStorage only (no server upload)
- FR-016: Widget MUST merge browser-local sessions with server-side sessions on Tier upgrade

**Pattern Reference**: Pattern 3 (Session Continuity with Tier Upgrades)

---

## Pre-Implementation Review

### Design Artifacts

- [ ] Read Pattern 3 (Session Continuity) in `.claude/skills/chatkit-widget/patterns.md` lines 267-418
- [ ] Review session merge flow diagram (patterns.md lines 330-352)
- [ ] Review privacy consent requirements (patterns.md lines 372-388, GDPR compliance)
- [ ] Review conflict resolution strategy (patterns.md lines 354-370)

### Event Schema Review

- [ ] Review `user_message` event schema (SKILL.md lines 86-104) - includes session_id
- [ ] Review `authentication_completed` event schema (SKILL.md lines 194-202) - triggers session merge
- [ ] Review session_id validation rules (mcp.json lines 45-48) - UUID format required

---

## Anonymous User Session Persistence (Tier 0)

### Session Creation

- [ ] Generate UUID v4 for `session_id` on first widget load
- [ ] Store `session_id` in browser localStorage with key: `chatkit_session_id`
- [ ] Set localStorage expiration: 30 days from creation (FR-005)
- [ ] Verify no server upload occurs for anonymous sessions (NFR-014)

**LocalStorage Schema**:
```json
{
  "chatkit_session_id": "uuid-v4-string",
  "chatkit_session_created": "2025-12-26T10:00:00.000Z",
  "chatkit_session_expires": "2026-01-25T10:00:00.000Z",
  "chatkit_tier": "anonymous"
}
```

---

### Conversation History Persistence

- [ ] Store conversation messages in localStorage with key: `chatkit_history`
- [ ] Message schema includes: `id`, `role` (user|agent|system), `content`, `timestamp`, `citations[]`
- [ ] Limit conversation history: Keep last 20 messages (configurable)
- [ ] Prune old messages: Remove messages >30 days old on load
- [ ] Verify total localStorage usage <5 MB (browser quota)

**Conversation History Schema**:
```json
{
  "chatkit_history": [
    {
      "id": "msg-uuid-1",
      "role": "user",
      "content": "What is embodied intelligence?",
      "timestamp": "2025-12-26T10:15:00.000Z",
      "citations": []
    },
    {
      "id": "msg-uuid-2",
      "role": "agent",
      "content": "Embodied intelligence refers to...",
      "timestamp": "2025-12-26T10:15:02.500Z",
      "citations": [
        {"id": "citation-1", "url": "/docs/module-2-embodied/embodied-intelligence#definition"}
      ]
    }
  ]
}
```

---

### Bookmarks & Preferences (Optional for Tier 0)

- [ ] Store bookmarked content (if enabled for anonymous users)
- [ ] Store UI preferences: `theme` (light|dark), `language` (en)
- [ ] Key: `chatkit_bookmarks`, `chatkit_preferences`

**Bookmarks Schema**:
```json
{
  "chatkit_bookmarks": [
    {
      "content_id": "module-2-embodied/embodied-intelligence",
      "timestamp": "2025-12-26T10:20:00.000Z"
    }
  ]
}
```

**Preferences Schema**:
```json
{
  "chatkit_preferences": {
    "theme": "dark",
    "language": "en"
  }
}
```

---

### Session Expiration & Cleanup

- [ ] Check expiration on widget load: If `chatkit_session_expires` < now, delete session
- [ ] Prompt user before deleting expired session: "Your session expired. Start a new conversation?"
- [ ] Clear expired data: Remove `chatkit_history`, `chatkit_bookmarks` for expired sessions
- [ ] Generate new `session_id` after expiration

---

## Authenticated User Session Sync (Tier 1+)

### Session Merge Trigger

- [ ] Listen for `authentication_completed` event (user signs up or logs in)
- [ ] Read browser-local session data from localStorage
- [ ] Verify user consent before uploading (GDPR compliance, patterns.md line 374)

**Consent Modal** (GDPR Requirement):
```text
Title: "Save Your Conversation?"
Message: "We'll securely store your conversation history on our servers so you can access it from any device. You can delete it anytime."
Actions:
  [Yes, Save My Conversation] → consent_granted
  [No, Keep It Local Only] → consent_denied
```

---

### Session Upload & Merge

- [ ] If consent granted: Upload browser-local session data to `/api/v1/session/merge`
- [ ] API request includes: `session_id` (anonymous), `user_id` (authenticated), `conversation_history`, `bookmarks`, `preferences`
- [ ] Server merges browser-local → server-side session
- [ ] Server returns merged session data + new `session_id` (server-issued)
- [ ] Widget updates localStorage with new `session_id`
- [ ] Widget clears old browser-local session (data now on server)

**Session Merge API Request** (design-level):
```json
{
  "anonymous_session_id": "uuid-v4-browser-generated",
  "user_id": "user-uuid-authenticated",
  "data": {
    "conversation_history": [...],
    "bookmarks": [...],
    "preferences": {...}
  }
}
```

**Session Merge API Response**:
```json
{
  "session_id": "uuid-v4-server-issued",
  "merged": true,
  "conversation_history": [...],  // Merged from browser-local + server-side
  "bookmarks": [...],
  "preferences": {...}
}
```

---

### Conflict Resolution (Multi-Device Scenarios)

- [ ] Handle duplicate bookmarks: Deduplicate by `content_id`, keep earliest timestamp
- [ ] Handle overlapping conversations: Merge by timestamp, sort chronologically
- [ ] Handle preference conflicts: Server-side preference wins (most recent)

**Deduplication Logic** (design-level):
```typescript
function deduplicateBookmarks(local: Bookmark[], server: Bookmark[]): Bookmark[] {
  const combined = [...local, ...server];
  const uniqueMap = new Map<string, Bookmark>();

  for (const bookmark of combined) {
    const existing = uniqueMap.get(bookmark.content_id);
    if (!existing || bookmark.timestamp < existing.timestamp) {
      uniqueMap.set(bookmark.content_id, bookmark);
    }
  }

  return Array.from(uniqueMap.values());
}
```

---

### Cross-Device Session Sync (Tier 1+)

- [ ] Authenticated users: Fetch session from server on widget load
- [ ] API endpoint: `GET /api/v1/session/{user_id}`
- [ ] Widget renders conversation history from server (not localStorage)
- [ ] Changes saved to server in real-time (auto-save after each message)

---

## Privacy & Compliance

### GDPR (General Data Protection Regulation)

- [ ] **Consent Required**: Display consent modal before uploading session to server (FR-019)
- [ ] **Data Export**: Provide "Export Data" button for authenticated users (FR-020)
- [ ] **Data Deletion**: Provide "Delete Account" button (FR-021, 30-day retention)
- [ ] **Retention Policy**: Delete inactive sessions after 30 days (mcp.json line 199)

---

### CCPA (California Consumer Privacy Act)

- [ ] **Do Not Sell**: Widget MUST NOT share data with third parties (NFR-013)
- [ ] **Opt-Out**: Provide "Do Not Sell My Data" option (even though no selling occurs)

---

### Anonymous Users (Tier 0)

- [ ] **No Personal Data**: Widget MUST NOT collect email, name, or identifiers (FR-018)
- [ ] **Browser-Local Only**: Session data stored in localStorage, never uploaded to server (NFR-014)
- [ ] **No Analytics**: Widget MUST NOT log message content for anonymous users (FR-039)

---

## Testing Checklist

### Anonymous Session Persistence

- [ ] **Test 1**: Create session → Close browser → Reopen → Verify session persists
- [ ] **Test 2**: Create session → Wait 31 days → Verify session expires
- [ ] **Test 3**: Send 10 messages → Reload page → Verify all 10 messages restored
- [ ] **Test 4**: Fill localStorage to 4.9 MB → Verify widget handles quota gracefully
- [ ] **Test 5**: Disable cookies → Verify widget shows warning but still works (ephemeral mode)

---

### Session Merge (Tier 0 → Tier 1)

- [ ] **Test 6**: Anonymous session with 5 messages → Sign up → Verify history merged to server
- [ ] **Test 7**: Deny consent → Verify session stays browser-local, no server upload
- [ ] **Test 8**: Sign up on Device A → Sign in on Device B → Verify same conversation appears
- [ ] **Test 9**: Bookmark content as anonymous → Sign up → Verify bookmarks merged
- [ ] **Test 10**: Set dark theme as anonymous → Sign up → Verify theme preference preserved

---

### Conflict Resolution

- [ ] **Test 11**: Bookmark same page on 2 devices → Sign in → Verify deduplicated (1 bookmark)
- [ ] **Test 12**: Send messages on 2 devices → Sign in → Verify chronological merge
- [ ] **Test 13**: Change theme on Device A, language on Device B → Sign in → Verify both preserved

---

### Cross-Device Sync

- [ ] **Test 14**: Send message on Device A → Open Device B → Verify message appears
- [ ] **Test 15**: Bookmark on Device A → Refresh Device B → Verify bookmark synced
- [ ] **Test 16**: Delete conversation on Device A → Verify deleted on Device B

---

### Privacy & Security

- [ ] **Test 17**: Verify GDPR consent modal appears before session upload
- [ ] **Test 18**: Export data → Verify JSON/Markdown download includes all messages
- [ ] **Test 19**: Delete account → Wait 30 days → Verify data purged from server
- [ ] **Test 20**: Verify no analytics events contain message content for Tier 0 users

---

## Performance Targets

| Metric | Target | Source |
|--------|--------|--------|
| Session Load Time (from localStorage) | ≤50ms | Pattern 2 (Progressive Loading) |
| Session Save Time (to localStorage) | ≤10ms | Pattern 3 (Session Continuity) |
| Session Merge API Response Time | ≤500ms | Pattern 3 (Session Continuity) |
| Conversation History Render (20 msgs) | ≤100ms | NFR-004 |

---

## Error Handling

### localStorage Quota Exceeded

- [ ] Catch `QuotaExceededError` when writing to localStorage
- [ ] Prune oldest messages (FIFO) to free space
- [ ] Notify user: "Storage full. Oldest messages removed to save new conversation."
- [ ] Fallback: Ephemeral mode (no persistence) if quota still exceeded

---

### Session Merge API Failure

- [ ] Retry with exponential backoff (3 attempts, 1s, 2s, 4s delays)
- [ ] If all retries fail: Keep session browser-local, notify user
- [ ] Error message: "Unable to sync conversation. Your history is still saved locally."
- [ ] User can retry manually: "Retry Sync" button

---

### Network Disconnection During Sync

- [ ] Detect network offline event (`navigator.onLine === false`)
- [ ] Queue session changes for upload when network restores
- [ ] Display sync status indicator: "Offline - Changes will sync when online"

---

## Implementation Notes

### LocalStorage Keys

```
chatkit_session_id         → UUID v4 string
chatkit_session_created    → ISO 8601 timestamp
chatkit_session_expires    → ISO 8601 timestamp (created + 30 days)
chatkit_tier               → "anonymous" | "lightweight" | "full" | "premium"
chatkit_history            → JSON array of messages
chatkit_bookmarks          → JSON array of bookmarked content
chatkit_preferences        → JSON object {theme, language}
```

### Session Lifecycle

```
1. Widget Load
   ↓
2. Check localStorage for chatkit_session_id
   ↓
3a. If exists AND not expired: Load session
3b. If expired: Delete session, generate new UUID
3c. If not exists: Generate new UUID
   ↓
4. Render conversation history from localStorage (anonymous) or server (authenticated)
   ↓
5. User sends message
   ↓
6. Append to chatkit_history, save to localStorage
   ↓
7. If authenticated: Auto-save to server
```

---

## References

- **Pattern 3 (Session Continuity)**: `.claude/skills/chatkit-widget/patterns.md` lines 267-418
- **Privacy Consent**: patterns.md lines 372-388
- **Conflict Resolution**: patterns.md lines 354-370
- **FR-005**: Widget persists sessions for 30 days
- **NFR-014**: Anonymous sessions browser-local only
- **FR-016**: Merge sessions on tier upgrade

---

**Status**: Design Checklist Complete ✅
**Next Step**: Implement session persistence logic (Phase 7+)
