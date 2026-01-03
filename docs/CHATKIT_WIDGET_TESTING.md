# ChatKit Widget Integration Testing Checklist

**Purpose**: Verify ChatKit widget is properly integrated into the Physical AI Book Docusaurus site

**Version**: 1.0
**Date**: 2026-01-03
**Widget Version**: v0.4.0-observability-complete

---

## Prerequisites ✅

Before testing, ensure:

- [ ] ChatKit backend is running at `http://localhost:8000`
- [ ] Widget is built in implementation repo (`packages/widget/dist/chatkit-widget.js` exists)
- [ ] Docusaurus site is running at `http://localhost:3000`
- [ ] Browser DevTools console is open (F12)

### Start Backend

```bash
cd /mnt/c/Users/assad/Desktop/CODE/chatkit-widget-implementation/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

**Expected**: Server running at http://localhost:8000

**Verify**:
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","database":"connected"}
```

### Start Docusaurus

```bash
cd /mnt/c/Users/assad/Desktop/CODE/Hackathon_01/physical-ai-book
npm start
```

**Expected**: Site running at http://localhost:3000

---

## Test 1: Widget Loading ✅

**Goal**: Verify widget script loads and element mounts

### Steps:

1. Open browser to http://localhost:3000
2. Open DevTools Console (F12)
3. Check for widget element:
   ```javascript
   document.querySelector('chatkit-widget')
   ```

### Expected Results:

- [ ] No CORS errors in console
- [ ] No 404 errors for `chatkit-widget.js`
- [ ] `document.querySelector('chatkit-widget')` returns element (not null)
- [ ] Widget visible in bottom-right corner
- [ ] Widget has proper styling (350px × 500px, rounded corners, shadow)

### Common Issues:

**Widget not visible**:
- Check if backend is serving widget at http://localhost:8000/widget/chatkit-widget.js
- Verify `docusaurus.config.ts` has correct script src
- Check browser console for errors

**CORS error**:
- Verify backend `.env` has `CORS_ORIGINS=http://localhost:3000,http://localhost:8000`
- Restart backend after .env changes

---

## Test 2: Widget Interaction ✅

**Goal**: Verify basic chat functionality

### Steps:

1. Widget should show chat interface (header, messages area, input)
2. Type a test message: "Hello"
3. Click Send button (or press Enter)

### Expected Results:

- [ ] Input field clears after sending
- [ ] User message appears in chat (blue, right-aligned)
- [ ] Loading indicator shows while waiting for response
- [ ] Bot response appears (gray, left-aligned)
- [ ] Messages auto-scroll to bottom

### Common Issues:

**No response from bot**:
- Check backend logs for errors
- Verify backend `/health` endpoint is healthy
- Check if Qdrant is configured (vectors may be empty, that's ok for now)

**Widget frozen**:
- Check browser console for JavaScript errors
- Verify widget script loaded completely
- Check Network tab for failed requests

---

## Test 3: RAG Functionality ✅

**Goal**: Verify widget queries the RAG backend

### Steps:

1. Ask a question about Physical AI:
   - "What is embodied intelligence?"
   - "Explain humanoid robotics"
   - "What are the key challenges in Physical AI?"

### Expected Results:

- [ ] Request sent to `http://localhost:8000/api/v1/chat`
- [ ] Response includes relevant content (if Qdrant has data)
- [ ] Citations shown (if available)
- [ ] Response time < 5 seconds

### Expected Behavior (No Vector Data):

If Qdrant collection is empty:
- [ ] Widget shows fallback response: "I couldn't find specific content..."
- [ ] No errors in console
- [ ] Widget remains functional

**Note**: To get real RAG responses, you need to import course content into Qdrant. See [QDRANT_SETUP_GUIDE.md](https://github.com/assadsharif/chatkit-widget-implementation/blob/main/docs/QDRANT_SETUP_GUIDE.md)

---

## Test 4: Responsive Design ✅

**Goal**: Verify widget adapts to different screen sizes

### Steps:

1. Test Desktop (>1024px):
   - [ ] Widget: 350px × 500px
   - [ ] Position: bottom-right corner (20px margins)

2. Test Tablet (769-1024px):
   - Resize browser to ~800px width
   - [ ] Widget: 320px × 450px
   - [ ] Position: bottom-right corner (15px margins)

3. Test Mobile (<768px):
   - Resize browser to ~375px width
   - [ ] Widget: Full screen (100vw × 100vh)
   - [ ] No border-radius
   - [ ] No margins

### Expected Results:

- [ ] Widget remains usable at all screen sizes
- [ ] No horizontal scrolling
- [ ] Text remains readable
- [ ] Buttons remain clickable

---

## Test 5: Dark Mode ✅

**Goal**: Verify widget theming adapts to Docusaurus dark mode

### Steps:

1. Click Docusaurus theme toggle (sun/moon icon in navbar)
2. Switch to dark mode
3. Observe widget appearance

### Expected Results:

- [ ] Widget background updates to dark theme
- [ ] Widget border/shadow adjusted for dark theme
- [ ] Primary color uses `--ifm-color-primary-light`
- [ ] Text remains readable
- [ ] Messages have proper contrast

---

## Test 6: Accessibility ✅

**Goal**: Verify keyboard navigation and screen reader support

### Steps:

1. **Keyboard Navigation**:
   - [ ] Tab key focuses input field
   - [ ] Enter key sends message
   - [ ] Escape key (if implemented) closes widget

2. **Screen Reader** (Optional):
   - Enable screen reader (NVDA, JAWS, or VoiceOver)
   - [ ] Widget elements announced properly
   - [ ] Message updates announced

3. **Focus Management**:
   - [ ] Focus visible on interactive elements
   - [ ] Focus trap within widget when modal/signup open

---

## Test 7: Performance ✅

**Goal**: Verify widget loads quickly and doesn't block page

### Steps:

1. Open DevTools → Network tab
2. Reload page (Ctrl+R or Cmd+R)
3. Check widget script load time

### Expected Results:

- [ ] `chatkit-widget.js` loads in < 500ms
- [ ] Widget is loaded `async` (doesn't block page render)
- [ ] Widget script size ~39KB (acceptable)
- [ ] Page interactive in < 2 seconds

---

## Test 8: Session Persistence ✅

**Goal**: Verify chat history persists across page refreshes

### Steps:

1. Send a few messages in chat
2. Refresh page (F5)
3. Check if messages reappear

### Expected Results (Anonymous Tier):

- [ ] Messages persist in browser localStorage
- [ ] Session ID remains same across refreshes
- [ ] Widget shows previous conversation

**Note**: Session is browser-local for anonymous users. Clearing localStorage will reset session.

---

## Test 9: Error Handling ✅

**Goal**: Verify graceful error handling

### Steps:

1. **Backend Down**:
   - Stop backend server
   - Try sending a message

   **Expected**:
   - [ ] Error message shown in widget
   - [ ] No uncaught exceptions in console
   - [ ] Widget remains functional

2. **Network Timeout**:
   - Slow down network (DevTools → Network → Throttling → Slow 3G)
   - Send message

   **Expected**:
   - [ ] Loading indicator shows
   - [ ] Timeout after ~30 seconds
   - [ ] Error message shown

3. **Invalid Input**:
   - Send empty message (should be blocked)
   - Send very long message (>5000 chars)

   **Expected**:
   - [ ] Empty messages rejected
   - [ ] Long messages truncated or rejected with error

---

## Test 10: Multi-Page Navigation ✅

**Goal**: Verify widget persists across page navigation

### Steps:

1. Send a message on homepage
2. Navigate to different docs page (e.g., click sidebar link)
3. Check widget state

### Expected Results:

- [ ] Widget remains visible on all pages
- [ ] Chat history persists across navigation
- [ ] No duplicate widget instances
- [ ] Widget state preserved (open/closed)

---

## Production Readiness Checklist 🚀

Before deploying to production:

### Configuration:

- [ ] Update widget API URL from `localhost` to production backend URL
- [ ] Backend deployed to production (Railway, Vercel, etc.)
- [ ] Neon Postgres configured for production
- [ ] Qdrant vector DB configured for production
- [ ] Environment variables set correctly

### Security:

- [ ] CORS restricted to production domain only
- [ ] HTTPS enabled for backend
- [ ] API keys rotated and secured
- [ ] Rate limiting enabled

### Performance:

- [ ] Widget minified and compressed
- [ ] CDN caching configured (if applicable)
- [ ] Backend performance tested under load

### Content:

- [ ] Course content imported into Qdrant
- [ ] Vector embeddings generated
- [ ] RAG retrieval tested and accurate

---

## Troubleshooting Guide

### Widget Not Loading

**Check**:
```bash
# Verify widget endpoint accessible
curl -I http://localhost:8000/widget/chatkit-widget.js

# Expected: HTTP/1.1 200 OK
```

**Fix**:
- Ensure backend is running
- Verify widget path in `backend/app/main.py` mounts correctly
- Check widget was built: `ls packages/widget/dist/chatkit-widget.js`

### CORS Errors

**Check backend logs**:
```
INFO:     127.0.0.1:xxxxx - "GET /widget/chatkit-widget.js HTTP/1.1" 200 OK
```

**Fix**:
```bash
# In backend/.env
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,https://yourdomain.com
```

### No RAG Responses

**Check Qdrant status**:
```bash
curl http://localhost:8000/api/v1/qdrant/status
```

**If vectors_count = 0**:
- Import course content (see QDRANT_SETUP_GUIDE.md)
- Widget will work but return generic responses

---

## Testing Summary

| Test | Status | Notes |
|------|--------|-------|
| Widget Loading | ⏳ Pending | Run this checklist |
| Widget Interaction | ⏳ Pending | |
| RAG Functionality | ⏳ Pending | Requires content import |
| Responsive Design | ⏳ Pending | |
| Dark Mode | ⏳ Pending | |
| Accessibility | ⏳ Pending | |
| Performance | ⏳ Pending | |
| Session Persistence | ⏳ Pending | |
| Error Handling | ⏳ Pending | |
| Multi-Page Navigation | ⏳ Pending | |

**Overall Integration Status**: ⏳ Ready for Testing

---

**References**:
- [ChatKit Implementation Repo](https://github.com/assadsharif/chatkit-widget-implementation)
- [Docusaurus Integration Guide](https://github.com/assadsharif/chatkit-widget-implementation/blob/main/DOCUSAURUS_INTEGRATION.md)
- [Local Development Guide](https://github.com/assadsharif/chatkit-widget-implementation/blob/main/LOCAL_DEVELOPMENT.md)
- [Design Freeze v1.0](https://github.com/assadsharif/Hackathon_01/tree/v1.0-design-freeze)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
