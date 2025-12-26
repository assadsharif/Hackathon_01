# Better-Auth MCP Server

**Type**: Design Intelligence MCP Server
**Source**: [Better-Auth Documentation](https://www.better-auth.com/)
**Status**: Active (Phase 5+)
**Created**: 2025-12-26

---

## Overview

The Better-Auth MCP Server provides **design-time authentication and authorization intelligence** for the Physical AI & Humanoid Robotics platform. This server enables AI agents to access Better-Auth design patterns, best practices, and architectural guidance when designing user authentication flows.

**Critical Distinction**: This is a **design intelligence server**, not a runtime authentication implementation. It provides conceptual guidance for spec-driven development phases.

---

## What is Better-Auth?

[Better-Auth](https://www.better-auth.com/) is a modern authentication framework that emphasizes:
- **Developer Experience**: Type-safe, framework-agnostic
- **Privacy-First**: Built-in GDPR/CCPA compliance
- **Flexible Auth Flows**: Email, OAuth, passwordless, magic links
- **Session Management**: Secure, scalable session handling
- **Role-Based Access Control**: Fine-grained permissions

This MCP server extracts Better-Auth's design philosophy for **academic specification work**.

---

## Capabilities

This MCP server provides design intelligence for:

### 1. Signup Flow Validation
- Progressive signup pattern validation
- Multi-tier onboarding flow design
- Privacy-first data collection strategies
- Age-gated signup (COPPA compliance)

### 2. Signin and Session Architecture
- Session-based vs. JWT-based design decisions
- Secure session storage patterns (cookies, LocalStorage, server-side)
- Session expiration and refresh token strategies
- Multi-device session management

### 3. OAuth and Passwordless Design Guidance
- Social login integration patterns (Google, GitHub, Microsoft)
- Magic link authentication flows
- Passwordless email verification
- Hybrid auth strategies (email + OAuth fallback)

### 4. Role-Based Access Control (RBAC) Patterns
- User role hierarchies (anonymous → authenticated → premium)
- Permission schemas for educational platforms
- Feature gating based on user tiers
- Admin panel access patterns

### 5. User Profiling for Personalization
- Profile data schema design
- Progressive profile enrichment
- Privacy-preserving personalization
- User preference management

### 6. Security Best Practices
- Password hashing and storage (argon2, bcrypt)
- CSRF protection patterns
- Rate limiting for auth endpoints
- Account enumeration prevention
- Secure password reset flows

### 7. Privacy-First Authentication Flows
- Anonymous-first architecture
- Minimal data collection principles
- GDPR right-to-deletion implementation
- CCPA "Do Not Sell" opt-out patterns
- FERPA compliance for educational platforms

---

## Supported Patterns

This MCP server supports design validation for:

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Progressive Signup** | Tier 0 → Tier 4 authentication levels | Educational platforms with optional personalization |
| **Passwordless Authentication** | Magic links, email verification | Reduced friction for learning platforms |
| **Email + OAuth Hybrid** | Primary email with social login fallback | Maximum user choice |
| **Session-based Auth** | Server-side session storage | Enhanced security for educational data |
| **JWT-based Auth** | Stateless authentication tokens | Scalable API authentication |
| **Privacy-first Identity Management** | Minimal PII collection, explicit consent | GDPR/CCPA/FERPA compliance |

---

## Integration Scope

### Current Integration: `signup-personalization` Skill

This MCP server directly supports the `.claude/skills/signup-personalization` skill by providing:
- Authentication flow design patterns
- Security best practices for user data
- Privacy-first architecture guidance
- Session management strategies

**Reference**: `.claude/skills/signup-personalization/SKILL.md`

### Future Integration Opportunities

**Educational Platforms**:
- Student authentication with FERPA compliance
- Instructor/admin role hierarchies
- Parent/guardian account linking (COPPA <13)

**Documentation Platforms**:
- Anonymous browsing with optional personalization
- Contributor authentication for wikis/docs
- API key management for external integrations

**SaaS Applications**:
- Multi-tenant authentication
- Enterprise SSO (SAML, OIDC)
- Usage-based access control

---

## Design-Time Usage

### How AI Agents Use This Server

When working on authentication-related design tasks, AI agents query this MCP server to:

1. **Validate Design Decisions**:
   - "Is this signup flow privacy-compliant?"
   - "Does this session strategy scale?"

2. **Generate Spec Recommendations**:
   - Suggest RBAC schemas for user tiers
   - Recommend OAuth providers for target audience

3. **Identify Security Gaps**:
   - Detect missing CSRF protection
   - Flag insecure password storage patterns

4. **Ensure Compliance**:
   - Verify GDPR right-to-access implementation
   - Check COPPA age-gating for <13 users

### Example Query Flow

**Agent Task**: "Design a signup flow for educational platform with FERPA compliance"

**MCP Server Response**:
```markdown
Recommended Pattern: Progressive Signup with Privacy-First Principles

Tier 0 (Anonymous):
- No PII collection
- LocalStorage-only session (browser-local)
- 30-day retention, auto-delete

Tier 1 (Email Signup):
- Email + hashed password (argon2)
- Server-side session storage
- Parental consent modal for users <18 (FERPA)

Tier 2 (Profile Customization):
- Optional: Name, learning goals, institution
- Explicit consent checkboxes (GDPR Article 7)
- Right to delete account (one-click)

Security Measures:
- Rate limiting: 5 signup attempts per IP per hour
- Email verification required before profile access
- Password strength: min 12 chars, complexity rules
- CSRF tokens for all POST requests

Compliance Checks:
- [x] FERPA: Parental consent for <18
- [x] GDPR: Explicit consent, right to delete
- [x] CCPA: "Do Not Sell" opt-out available
```

---

## File Structure

```
.claude/mcp/better-auth/
├── mcp.json           # MCP server configuration
├── README.md          # This file
└── patterns/          # (Future) Design pattern library
    ├── progressive-signup.md
    ├── oauth-hybrid.md
    └── privacy-first-rbac.md
```

---

## Academic Scope Constraints

**What This MCP Server DOES**:
- Provide design patterns and best practices
- Validate authentication flow designs
- Suggest security and privacy improvements
- Reference Better-Auth documentation for design decisions

**What This MCP Server DOES NOT DO**:
- Generate runtime authentication code
- Implement actual auth endpoints
- Manage user credentials
- Handle production authentication requests

**Phase Alignment**: This server is used during **specification and planning phases** (spec.md, plan.md), NOT implementation.

---

## References

### Better-Auth Documentation
- **Official Site**: https://www.better-auth.com/
- **GitHub**: https://github.com/better-auth/better-auth
- **Docs**: https://www.better-auth.com/docs

### Related Project Artifacts
- **Signup Personalization Skill**: `.claude/skills/signup-personalization/SKILL.md`
- **Progressive Enhancement Pattern**: `.claude/skills/signup-personalization/patterns.md#pattern-1`
- **Privacy-First Data Management**: `.claude/skills/signup-personalization/patterns.md#pattern-3`

### Compliance Resources
- **GDPR**: https://gdpr.eu/
- **CCPA**: https://oag.ca.gov/privacy/ccpa
- **FERPA**: https://www2.ed.gov/policy/gen/guid/fpco/ferpa/index.html
- **COPPA**: https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-26 | Initial MCP server configuration for Phase 5 |

---

## Future Enhancements

**Planned Expansions**:
1. **Pattern Library**: Add `/patterns` directory with detailed design patterns
2. **Compliance Checklist Templates**: GDPR/CCPA/FERPA validation checklists
3. **Security Audit Scripts**: Automated design review for common auth vulnerabilities
4. **Integration Examples**: Reference architectures for Docusaurus, Next.js, SvelteKit

---

**Created**: 2025-12-26
**Maintained By**: Academic Spec-Driven Development Project
**License**: Documentation Only (No Code)
