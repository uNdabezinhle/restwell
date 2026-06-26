# RestWell – Technical Planning for v1 Differentiators

**Date**: June 2026  
**Focus Areas**: Custom Branding Engine, Branded Client Mobile App Generator, Client Website + Website Builder

---

## 1. Custom Branding Engine (High Priority)

### Goal
Allow each tenant (funeral parlor or future stakeholder) to fully customize the look and feel of the platform with their own branding.

### Key Requirements (v1)
- Upload logo (with automatic resizing for different contexts)
- Choose primary/secondary colors (with accessibility checks)
- Custom domain support (e.g., app.clientname.co.za)
- Branded email templates and SMS sender names
- White-label removal of "Powered by RestWell" in higher tiers

### Technical Approach
- **Frontend (Flutter)**: Dynamic theming using `ThemeData` + provider/riverpod for runtime theme switching.
- **Backend (Django)**: 
  - New model: `TenantBranding` with fields for logo, colors, domain, email settings.
  - Middleware that injects branding context based on `tenant_id`.
- **Storage**: Use S3-compatible storage (or local) for logos.
- **Challenges**: 
  - Ensuring consistent theming across web, mobile, and generated apps.
  - Handling email branding reliably.

**Estimated Effort**: Medium-High (core feature)

---

## 2. Branded Client Mobile App Generator

### Goal
Automatically generate and distribute a fully branded native mobile app (Android + iOS) for each client.

### Key Requirements (v1)
- Client can request a branded version of the RestWell client-facing app.
- App includes their logo, colors, and name.
- Distribution via Google Play / Apple App Store or TestFlight / internal distribution initially.
- Basic configuration (e.g., which modules are visible).

### Technical Approach (Recommended for v1)
**Option A (Faster for v1)**: 
- Use **Flutter + Codemagic / GitHub Actions** to create a CI/CD pipeline.
- Each tenant gets a configuration file.
- Build process generates a custom APK/IPA with their branding injected at build time.
- Start with Android (easier distribution) and add iOS later.

**Option B (More scalable long-term)**:
- Use a white-label app framework or Flutter + flavors + dynamic configuration.

**v1 Recommendation**: Start with **Android APK generation** via automated build pipeline + manual review. Offer iOS in later phase or via TestFlight for early clients.

**Challenges**:
- App Store review process for each branded app (initially use internal distribution or enterprise distribution).
- Keeping the core codebase clean while supporting many branded variants.

**Estimated Effort**: High (but very high value)

---

## 3. Client Website + Website Builder

### Goal
Provide each client with a public-facing website (memorial pages, service information, booking inquiries) that they can easily manage.

### Key Requirements (v1)
- Simple drag-and-drop or form-based website builder.
- Pre-built templates (funeral home, memorial, etc.).
- Domain management (connect custom domain or use RestWell subdomain).
- Integration with core platform (e.g., show upcoming services, allow basic inquiries).
- Mobile-responsive by default.

### Technical Approach
**Recommended Stack for v1**:
- **Backend**: Django + Wagtail CMS or a lightweight custom page builder using Django + HTMX + Tailwind.
- **Frontend**: Modern responsive templates (Tailwind + Alpine.js or simple React components).
- **Domain Management**: Integrate with a DNS provider (e.g., Cloudflare API or similar) for custom domains.
- **Hosting**: Static site generation or server-side rendering on the same infrastructure.

**Alternative (Faster MVP)**:
- Use an embedded solution or partner with a white-label website builder initially, then build native later.

**v1 Recommendation**: Build a **simple but powerful** page builder focused on funeral-specific needs (memorial pages, service schedules, contact forms) rather than a full general-purpose builder.

**Estimated Effort**: Medium

---

## Overall Technical Recommendations for v1

| Feature                    | Priority | Recommended Approach for v1          | Effort   | Notes |
|---------------------------|----------|--------------------------------------|----------|-------|
| Custom Branding Engine    | High     | Dynamic theming + TenantBranding model | Medium-High | Start here |
| Branded Client App        | High     | Flutter CI/CD pipeline (Android first) | High     | Biggest differentiator |
| Client Website + Builder  | Medium   | Django + simple page builder         | Medium   | Focus on funeral-specific templates |

### Suggested Implementation Order (v1)
1. **Custom Branding Engine** (foundational – affects everything else)
2. **Client Website + Website Builder**
3. **Branded Client Mobile App Generator** (can start with Android + manual builds, then automate)

### Risks & Mitigation
- **App Store complexity**: Start with Android + internal distribution / TestFlight.
- **Scope creep on Website Builder**: Keep v1 focused on funeral-specific pages (memorials, services, contact).
- **Branding consistency**: Invest early in a strong design system.

---

## Next Technical Steps

- Create Django models for `TenantBranding`
- Design Flutter theming architecture
- Research Flutter build automation options (Codemagic, GitHub Actions, or Fastlane)
- Define MVP scope for the Website Builder (what templates and features are essential)

This technical foundation will make RestWell significantly more valuable and defensible than competitors.

---

**Document Status**: Initial Technical Planning – Ready for review and iteration.