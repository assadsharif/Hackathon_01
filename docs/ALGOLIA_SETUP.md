# Algolia DocSearch Setup Guide

This guide walks you through setting up Algolia DocSearch for the Physical AI & Humanoid Robotics Book.

**Status**: ⏳ Pending Application
**Priority**: High
**Effort**: ~30 minutes (application) + 1-3 days (approval)

---

## What is Algolia DocSearch?

Algolia DocSearch is a **free** search service for open-source documentation projects. It provides:

- ⚡ **Lightning-fast search** - Results in <50ms
- 🔍 **Intelligent ranking** - Most relevant results first
- 🎯 **Typo tolerance** - Finds results even with misspellings
- 📊 **Search analytics** - Understand what users search for
- 🎨 **Beautiful UI** - Modern search modal with keyboard shortcuts
- 🆓 **Free for open-source** - No cost for public projects

**Current Search**: Docusaurus default (basic client-side search)
**With Algolia**: Advanced server-side search with better results

---

## Step 1: Apply for DocSearch

### Prerequisites

✅ Your project qualifies because:
- It's **publicly accessible** (GitHub Pages)
- It's **open-source** (public repository)
- It's **documentation** (educational content)
- You are the **owner/maintainer** of the project

### Application Process

**1. Go to DocSearch Application:**
```
https://docsearch.algolia.com/apply/
```

**2. Fill in the form:**

| Field | Value |
|-------|-------|
| **Website URL** | `https://assadsharif.github.io/Hackathon_01/` |
| **Email** | Your email address (GitHub email recommended) |
| **Repository URL** | `https://github.com/assadsharif/Hackathon_01` |
| **Documentation URL** | `https://assadsharif.github.io/Hackathon_01/` |

**3. Additional Information (form field):**

```
Project Name: Physical AI & Humanoid Robotics Book
Project Description:
A comprehensive open-source educational book on embodied intelligence
and humanoid robotics. Covers 7 modules from foundations of physical AI
to future applications. Built with Docusaurus, intended for AI students
and robotics engineers.

I am the maintainer of this documentation project and have read the
checklist above.
```

**4. Agree to terms:**
- ✅ Your website is publicly available
- ✅ You are the owner/maintainer
- ✅ The content is technical documentation
- ✅ DocSearch will be the primary search

**5. Submit application**

### What Happens Next?

**Timeline:**
- Application reviewed: 1-3 business days
- Approval email sent with credentials
- Algolia team sets up initial indexing

**Approval Email Contains:**
- `appId` - Your Algolia application ID
- `apiKey` - Your public search-only API key
- `indexName` - Index name (usually your domain/project name)

---

## Step 2: Configure Docusaurus

### After Approval

**1. Update `docusaurus.config.ts`:**

Open `physical-ai-book/docusaurus.config.ts` and replace the placeholder values:

```typescript
algolia: {
  appId: 'ABC123XYZ',           // Replace with your appId
  apiKey: 'abc123...',          // Replace with your search API key
  indexName: 'physical-ai-book', // Replace with your index name
  contextualSearch: true,
  searchPagePath: 'search',
},
```

**2. Test locally:**

```bash
cd physical-ai-book
npm run start
```

- Open http://localhost:3000
- Press `/` or `Ctrl+K` to open search
- You should see "Searching..." (may have no results locally)

**3. Deploy to production:**

```bash
git add docusaurus.config.ts
git commit -m "feat: enable Algolia DocSearch"
git push origin 001-physical-ai-book
```

**4. Wait for deployment:**
- GitHub Actions builds and deploys
- Algolia crawler indexes your site (runs automatically)
- Search will be available within 24 hours of first deployment

---

## Step 3: Configure Crawler (Optional)

### Default Configuration

Algolia's crawler will automatically index your site using DocSearch defaults. No configuration needed for basic functionality.

### Custom Configuration (Advanced)

If you need to customize what gets indexed:

**1. Access Crawler Admin:**
- You'll receive a link to the Algolia Crawler admin panel
- Login with your email

**2. Edit crawler config:**

```json
{
  "index_name": "physical-ai-book",
  "start_urls": [
    "https://assadsharif.github.io/Hackathon_01/"
  ],
  "sitemap_urls": [
    "https://assadsharif.github.io/Hackathon_01/sitemap.xml"
  ],
  "selectors": {
    "lvl0": {
      "selector": ".menu__link--sublist.menu__link--active",
      "global": true,
      "default_value": "Documentation"
    },
    "lvl1": "article h1",
    "lvl2": "article h2",
    "lvl3": "article h3",
    "lvl4": "article h4",
    "lvl5": "article h5",
    "text": "article p, article li"
  }
}
```

**When to customize:**
- Need to exclude certain pages
- Want to index additional metadata
- Need to adjust ranking priorities

---

## Step 4: Verify Search Works

### Testing Checklist

**After deployment and indexing:**

**1. Basic Search:**
- [ ] Go to deployed site
- [ ] Press `/` or `Ctrl+K`
- [ ] Search modal opens
- [ ] Try searching: "embodied cognition"
- [ ] Results appear

**2. Search Features:**
- [ ] Keyboard navigation (arrow keys)
- [ ] Hit `Enter` to navigate to result
- [ ] Press `Esc` to close modal
- [ ] Search highlights in content

**3. Search Quality:**
- [ ] Search for misspelled terms (e.g., "humaniod" → "humanoid")
- [ ] Search for partial terms (e.g., "percep" → "perception")
- [ ] Search for synonyms
- [ ] Verify most relevant results appear first

**4. Mobile Search:**
- [ ] Open site on mobile (375px viewport)
- [ ] Tap search icon
- [ ] Search works on mobile
- [ ] Results are touch-friendly

---

## Features You'll Get

### 1. Smart Search Modal

**Keyboard Shortcuts:**
- `/` or `Ctrl+K` - Open search
- `↑`/`↓` - Navigate results
- `Enter` - Open selected result
- `Esc` - Close search

**Visual Features:**
- Recent searches
- Search suggestions
- Highlighted keywords
- Categorized results (by module)

### 2. Search Analytics

**Access at**: https://www.algolia.com/apps/YOUR_APP_ID/dashboard

**Metrics:**
- Top search queries
- No-result searches (identify missing content)
- Click-through rate
- User engagement

**Use analytics to:**
- Understand what users look for
- Identify gaps in content
- Improve content based on queries

### 3. Advanced Features

**Typo Tolerance:**
```
User types: "humanod robotcs"
Finds: "humanoid robotics"
```

**Contextual Search:**
```
When viewing Module 2, prioritize Module 2 results
```

**Faceted Search:**
```
Filter by: Module, Chapter, Topic
```

---

## Troubleshooting

### Issue: Application Rejected

**Reasons:**
- Site not publicly accessible yet
- Not enough content (too early in development)
- Not technical documentation

**Solution:**
- Ensure site is deployed and accessible
- Wait until more content is published
- Reapply after deployment complete

### Issue: Search Returns No Results

**Possible Causes:**
1. Indexing not complete yet (wait 24 hours)
2. Crawler hasn't run (check Algolia dashboard)
3. Wrong index name in config

**Debug Steps:**
```bash
# Check crawler status
# Go to: https://crawler.algolia.com/admin/crawlers

# Verify index exists
# Go to: https://www.algolia.com/apps/YOUR_APP_ID/indices
```

### Issue: Search is Slow

**Unlikely** - Algolia is typically <50ms
**If slow:**
- Check network (not Algolia issue)
- Check browser console for errors
- Verify correct `apiKey` (not admin key)

### Issue: Search Modal Doesn't Open

**Debug:**
```javascript
// Open browser console (F12)
// Check for errors

// Verify Algolia loaded
console.log(window.docsearch);
```

**Common fixes:**
- Clear cache and reload
- Check `apiKey` is correct
- Verify site is deployed (not localhost)

---

## Configuration Reference

### Basic Configuration

```typescript
algolia: {
  appId: 'YOUR_APP_ID',
  apiKey: 'YOUR_SEARCH_API_KEY',
  indexName: 'physical-ai-book',
}
```

### Advanced Configuration

```typescript
algolia: {
  appId: 'YOUR_APP_ID',
  apiKey: 'YOUR_SEARCH_API_KEY',
  indexName: 'physical-ai-book',

  // Contextual search (search within current section)
  contextualSearch: true,

  // Custom search parameters
  searchParameters: {
    facetFilters: ['language:en', 'version:1.0'],
  },

  // Search page path
  searchPagePath: 'search',

  // Insights (track click analytics)
  insights: true,

  // Disable if you don't want the search page
  // searchPagePath: false,
}
```

### Environment Variables (Advanced)

For multiple environments:

```typescript
// docusaurus.config.ts
algolia: {
  appId: process.env.ALGOLIA_APP_ID || 'YOUR_APP_ID',
  apiKey: process.env.ALGOLIA_API_KEY || 'YOUR_SEARCH_API_KEY',
  indexName: 'physical-ai-book',
}
```

---

## Timeline

### Expected Schedule

| Phase | Duration | Status |
|-------|----------|--------|
| **1. Apply** | 10 minutes | ⏳ Pending |
| **2. Wait for Approval** | 1-3 days | ⏳ Pending |
| **3. Configure & Deploy** | 15 minutes | ⏳ Pending |
| **4. First Indexing** | 24 hours | ⏳ Pending |
| **5. Verify & Test** | 10 minutes | ⏳ Pending |
| **Total** | ~2-4 days | ⏳ In Progress |

---

## Alternative: Manual Setup (Not Recommended)

If DocSearch application is rejected or delayed, you can set up Algolia manually:

**Requirements:**
- Algolia account (free tier)
- Manual index creation
- Custom crawler setup or manual indexing

**Why not recommended:**
- More complex setup
- Manual maintenance required
- No free tier benefits
- DocSearch is purpose-built for docs

**Better approach:** Wait for DocSearch approval (almost always approved for legitimate open-source projects)

---

## Post-Setup Optimization

### After Search is Live

**1. Monitor Analytics (Weekly)**
- Check top search queries
- Identify no-result searches
- Add missing content for common queries

**2. Improve Search Quality**
- Ensure all pages have proper headings
- Add keywords to meta descriptions
- Use consistent terminology

**3. Promote Search Usage**
- Add search tips to homepage
- Mention keyboard shortcut (`/`)
- Highlight in documentation

---

## Resources

**Algolia DocSearch:**
- Application: https://docsearch.algolia.com/apply/
- Documentation: https://docsearch.algolia.com/docs/what-is-docsearch
- FAQ: https://docsearch.algolia.com/docs/faq

**Docusaurus Integration:**
- Search Docs: https://docusaurus.io/docs/search
- Algolia Config: https://docusaurus.io/docs/api/themes/configuration#algolia

**Algolia Dashboard:**
- Login: https://www.algolia.com/users/sign_in
- Analytics: https://www.algolia.com/apps/YOUR_APP_ID/analytics

---

## Next Steps

**Immediate Actions:**

1. ✅ Configuration added to `docusaurus.config.ts`
2. ⏳ **Apply for DocSearch** at https://docsearch.algolia.com/apply/
3. ⏳ Wait for approval email (1-3 days)
4. ⏳ Update config with actual credentials
5. ⏳ Deploy and test

**After Setup:**
- Monitor search analytics monthly
- Optimize content based on search queries
- Promote search feature to users

---

**Document Status**: Ready for application
**Last Updated**: 2025-12-24
**Estimated Completion**: 2-4 days after application
