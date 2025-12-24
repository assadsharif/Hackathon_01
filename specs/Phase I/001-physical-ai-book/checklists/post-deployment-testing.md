# Post-Deployment Testing Checklist

**Phase**: Phase 6 - Final Validation (T090-T091)
**Purpose**: Verify performance, accessibility, and user experience on deployed site
**Site URL**: `https://assadsharif.github.io/Hackathon_01/`
**Date**: 2025-12-24

---

## Prerequisites

**Before Running These Tests:**
- ✅ Site deployed to GitHub Pages
- ✅ DNS propagation complete (may take 5-10 minutes)
- ✅ Site accessible at production URL
- ⏳ Initial deployment workflow succeeded

**Verify Deployment:**
```bash
# Check if site is live
curl -I https://assadsharif.github.io/Hackathon_01/

# Expected: HTTP 200 OK
```

---

## T090: Lighthouse Performance Audit (SC-003)

### Success Criteria
**SC-003**: Page load time < 3 seconds on standard connections

### Testing Method

**Option 1: Chrome DevTools Lighthouse (Recommended)**

1. Open Chrome browser
2. Navigate to `https://assadsharif.github.io/Hackathon_01/`
3. Open DevTools (F12 or Right-click → Inspect)
4. Go to "Lighthouse" tab
5. Configuration:
   - ✅ Performance
   - ✅ Accessibility
   - ✅ Best Practices
   - ✅ SEO
   - Device: **Mobile** (test mobile first)
   - Mode: Navigation (default)
6. Click "Analyze page load"
7. Wait for audit to complete (30-60 seconds)

**Option 2: PageSpeed Insights (Web)**

1. Go to: https://pagespeed.web.dev/
2. Enter URL: `https://assadsharif.github.io/Hackathon_01/`
3. Click "Analyze"
4. Review both Mobile and Desktop results

**Option 3: Lighthouse CI (Command Line)**

```bash
# Install Lighthouse globally
npm install -g lighthouse

# Run audit
lighthouse https://assadsharif.github.io/Hackathon_01/ \
  --output html \
  --output-path ./lighthouse-report.html \
  --view

# Mobile audit
lighthouse https://assadsharif.github.io/Hackathon_01/ \
  --preset=mobile \
  --output json \
  --output-path ./lighthouse-mobile.json
```

### Expected Results

**Performance Metrics (Mobile):**
- [ ] Performance Score: ≥90 (Target: 95+)
- [ ] First Contentful Paint (FCP): <1.8s
- [ ] Largest Contentful Paint (LCP): <2.5s
- [ ] Time to Interactive (TTI): <3.8s
- [ ] Total Blocking Time (TBT): <200ms
- [ ] Cumulative Layout Shift (CLS): <0.1

**Performance Metrics (Desktop):**
- [ ] Performance Score: ≥95 (Target: 98+)
- [ ] First Contentful Paint (FCP): <0.9s
- [ ] Largest Contentful Paint (LCP): <1.2s
- [ ] Time to Interactive (TTI): <2.5s

**Why We Should Pass:**
- ✅ Static site (no server-side rendering delays)
- ✅ Docusaurus optimized build (code splitting, lazy loading)
- ✅ No heavy images or videos
- ✅ Minimal custom CSS/JS
- ✅ GitHub Pages CDN (fast global delivery)

### Accessibility Score

**Expected:**
- [ ] Accessibility Score: ≥95
- [ ] All images have alt text
- [ ] Proper heading hierarchy (H1 → H2 → H3)
- [ ] Color contrast meets WCAG AA standards
- [ ] Interactive elements are keyboard accessible

### Best Practices & SEO

**Expected:**
- [ ] Best Practices Score: ≥90
- [ ] SEO Score: ≥90
- [ ] HTTPS enabled
- [ ] No console errors
- [ ] Mobile-friendly viewport

### Test Multiple Pages

**Pages to Audit:**
1. [ ] Homepage: `https://assadsharif.github.io/Hackathon_01/`
2. [ ] Module 1: `.../module-1-intro/`
3. [ ] Module 4: `.../module-4-perception/`
4. [ ] Module 7: `.../module-7-future/`

**Why**: Ensure consistent performance across different content pages

### Results Template

```markdown
## Lighthouse Audit Results

**Date**: [Date]
**Device**: Mobile / Desktop
**Page**: [URL]

### Scores:
- Performance: __/100
- Accessibility: __/100
- Best Practices: __/100
- SEO: __/100

### Core Web Vitals:
- FCP: __s
- LCP: __s
- TBT: __ms
- CLS: __

### Issues Found:
- [List any issues]

### Recommendations:
- [Any optimization suggestions]
```

---

## T091: Keyboard Navigation Testing (SC-005)

### Success Criteria
**SC-005**: Keyboard navigation works (Tab through sidebar, access all content)

### Testing Method

**Manual Keyboard Testing:**

1. Open deployed site: `https://assadsharif.github.io/Hackathon_01/`
2. Click in browser address bar (to reset focus)
3. Press `Tab` repeatedly
4. Observe focus indicators on interactive elements

**Keyboard Commands to Test:**

| Key | Expected Behavior |
|-----|-------------------|
| `Tab` | Move focus to next interactive element |
| `Shift+Tab` | Move focus to previous element |
| `Enter` | Activate focused link or button |
| `Space` | Scroll page down (on body) |
| `/` | Focus search box (if search enabled) |
| `Esc` | Close mobile menu / modal |

### Test Checklist

#### Desktop Navigation (>996px)

**Navbar:**
- [ ] Tab to GitHub link (top-right)
- [ ] Enter activates link
- [ ] Focus visible (outline or highlight)

**Sidebar:**
- [ ] Tab to first module heading
- [ ] Tab through all 7 modules
- [ ] Tab to each chapter link
- [ ] Enter opens chapter
- [ ] Collapsed sections expand on Enter
- [ ] Focus visible on all sidebar items

**Main Content:**
- [ ] Tab to "Edit this page" link (bottom)
- [ ] Tab to "Next page" navigation
- [ ] All in-page links accessible via Tab

**Footer:**
- [ ] Tab to footer links
- [ ] All footer items accessible

#### Mobile Navigation (<996px)

**Test in Chrome DevTools responsive mode (375px width):**

- [ ] Tab to hamburger menu icon
- [ ] Enter opens sidebar overlay
- [ ] Tab through sidebar items
- [ ] Enter selects chapter (sidebar closes)
- [ ] Esc closes sidebar
- [ ] Focus trapped in sidebar when open

### Accessibility Features to Verify

**Focus Indicators:**
- [ ] All interactive elements show focus state
- [ ] Focus indicator visible (not removed by CSS)
- [ ] Focus indicator has sufficient contrast

**Skip Links:**
- [ ] "Skip to main content" link present (optional)
- [ ] Works with keyboard (Tab → Enter)

**ARIA Attributes:**
- [ ] Sidebar has proper ARIA roles
- [ ] Hamburger menu has aria-label
- [ ] Collapsible sections have aria-expanded

**Heading Structure:**
- [ ] Logical heading hierarchy (H1 → H2 → H3)
- [ ] No skipped heading levels
- [ ] One H1 per page

### Screen Reader Testing (Optional)

**Test with NVDA (Windows) or VoiceOver (Mac):**

1. Enable screen reader
2. Navigate through sidebar using arrow keys
3. Verify module and chapter titles are announced
4. Verify links have descriptive labels
5. Verify page structure is logical

**Expected Results:**
- All content accessible via screen reader
- Navigation structure announced correctly
- Links have meaningful labels (not "click here")

### Test Multiple Browsers

**Browsers to Test:**
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if on Mac)

**Why**: Keyboard behavior can vary slightly between browsers

### Results Template

```markdown
## Keyboard Navigation Test Results

**Date**: [Date]
**Browser**: [Browser name and version]
**Viewport**: Desktop / Mobile

### Desktop Navigation:
- Navbar accessible: ✅ / ❌
- Sidebar accessible: ✅ / ❌
- Main content accessible: ✅ / ❌
- Footer accessible: ✅ / ❌
- Focus indicators visible: ✅ / ❌

### Mobile Navigation:
- Hamburger menu accessible: ✅ / ❌
- Sidebar overlay accessible: ✅ / ❌
- Esc closes sidebar: ✅ / ❌

### Issues Found:
- [List any keyboard accessibility issues]

### WCAG Compliance:
- Level A: ✅ / ❌
- Level AA: ✅ / ❌ (Target)
```

---

## Additional Post-Deployment Checks

### Search Functionality

**If Docusaurus search is enabled:**
- [ ] Search box accessible via keyboard (`/` shortcut)
- [ ] Tab through search results
- [ ] Enter selects result
- [ ] Esc closes search

### Mobile Responsiveness (from Phase 5)

**Complete Phase 5 tests after deployment:**
- [ ] T077: 375px viewport testing
- [ ] T078: Mobile sidebar interaction
- [ ] T079: Viewport meta tag verification
- [ ] T080: Mobile testing results documented

### Content Verification

**Spot Check Content:**
- [ ] All 7 modules visible in sidebar
- [ ] Homepage loads correctly
- [ ] Module index pages show learning outcomes
- [ ] Chapter content displays properly
- [ ] Cross-reference links work
- [ ] Images load (if any)

### Build Verification

**GitHub Actions:**
- [ ] Workflow completed successfully
- [ ] Build logs show no errors
- [ ] Deployment step succeeded
- [ ] No unexpected warnings

**Check at**: `https://github.com/assadsharif/Hackathon_01/actions`

---

## Success Criteria Summary

### Phase 6 Final Validation

**T090: Lighthouse Audit (SC-003)**
- ⏳ Performance Score ≥90 (Mobile)
- ⏳ Page load < 3 seconds
- ⏳ Core Web Vitals pass
- Status: **Pending deployment**

**T091: Keyboard Navigation (SC-005)**
- ⏳ All interactive elements accessible via Tab
- ⏳ Focus indicators visible
- ⏳ Sidebar navigable with keyboard
- Status: **Pending deployment**

**Overall Phase 6 Status:**
- 9/12 tasks complete (pre-deployment)
- 3/12 tasks pending (require live site)

---

## Next Steps After Testing

1. **Document Results:**
   - Fill in results templates above
   - Screenshot Lighthouse scores
   - Note any issues found

2. **Update Task Status:**
   - Mark T090 complete in tasks.md
   - Mark T091 complete in tasks.md
   - Update deployment-validation.md

3. **Address Issues (if any):**
   - Create follow-up tasks for fixes
   - Document workarounds
   - Plan optimization improvements

4. **Final Sign-Off:**
   - Verify all Phase 1-6 tasks complete
   - Update project status documentation
   - Celebrate successful deployment! 🎉

---

## Troubleshooting

### If Performance Score Low (<90):

**Common Issues:**
- Large image files → Use WebP or optimize images
- Unoptimized fonts → Use system fonts or font-display:swap
- Too much JavaScript → Review custom code
- Slow server response → Check GitHub Pages status

**For Static Docusaurus Site:**
- Should NOT have performance issues
- If score <90, likely GitHub Pages temporary issue
- Re-run audit after 5-10 minutes

### If Keyboard Navigation Fails:

**Common Issues:**
- Focus indicators removed by custom CSS
- Interactive elements not keyboard-accessible
- Focus trap not working in modal

**For Default Docusaurus:**
- Should pass all keyboard tests
- If failing, likely custom CSS issue
- Review src/css/custom.css for focus styles

---

**Document Status**: Ready for post-deployment testing
**Last Updated**: 2025-12-24
**Testing ETA**: 5-10 minutes after GitHub Pages deployment
