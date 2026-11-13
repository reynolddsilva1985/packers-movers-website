# Movers4Less technical review

**Review baseline:** `main` branch, 13 November 2026  
**Scope:** repository source, page structure, shared CSS/JavaScript, sitemap, launch safeguards and deployment design.  
**Production safety:** no customer-facing source files, DNS records, domain settings, hosting settings or production deployments were changed during this review.

## Executive assessment

Movers4Less is currently a lightweight static website, not a web application. That is a sensible choice for an early-stage removals business. It loads pages directly rather than running a large front-end framework, has no application server, does not accept enquiries and does not process payments.

The strongest existing decisions are:
- all customer-facing pages display a prominent concept-stage notice;
- the quote/enquiry form is disabled at the fieldset level;
- the estimate calculator runs in the visitor's browser and uses fixed selection lists;
- the website source contains no analytics or advertising tracker installation;
- the design uses vector artwork (inline SVG and an SVG favicon), not large raster photographs;
- the mobile menu has explicit expanded state and supports Escape, outside-click closure and resize handling;
- the site includes a not-found page, robots file and XML sitemap.

The main weakness is not the choice of HTML, CSS and JavaScript. It is the maintenance process around them. Common navigation, banner and footer markup is repeated across many HTML files, and the shared stylesheet has accumulated later visual overrides. Without automated checks, a small edit can unintentionally break a page or make common elements inconsistent.

**Recommendation:** keep the public website static for now. Improve its quality controls before introducing a framework or a backend. Do not start taking enquiries until the business, data handling and operational launch checks are complete.

## 1. What was inspected

The current site contains 20 HTML pages: homepage, service hub, five service pages, pricing, estimate, guides hub and three guide pages, areas, how-it-works, about, FAQs, enquiry preview, privacy and 404.

Shared files include:
- `styles.css` — site-wide presentation and responsive layouts;
- `script.js` — mobile navigation, footer year and estimate calculator;
- `favicon.svg` — vector brand icon;
- `robots.txt` and `sitemap.xml` — search-engine discovery;
- `BUSINESS-PLAN.md`, `PRICE-BOOK.md` and `LAUNCH-CHECKLIST.md` — internal planning documents;
- `CNAME` — the custom domain file.

The repository contains no app framework, package manifest or backend source in the reviewed main-branch files. That keeps the dependency and runtime surface small.

## 2. Customer journey and current functionality

| Journey | Current behaviour | Assessment |
|---|---|---|
| Understand the business | Homepage explains the affordability and reuse proposition and clearly labels the service as a concept | Good |
| Explore services | Dedicated pages for home moves, small moves, packing, fragile/bulky items and office moves | Good structure |
| Understand prices | Indicative price guide, with explicit caveats and VAT uncertainty | Useful, but must stay labelled as draft pricing |
| Estimate a move | Browser-only calculator based on anonymous dropdown selections | Appropriate for concept stage |
| Request a quote | Enquiry preview only; every field is disabled | Correctly prevents accidental collection |
| Book or pay | Not available | By design, not a defect |
| Privacy | Page explains current limitations and future launch requirements | Correctly says it is not a full business privacy notice |

The current website must not be mistaken for a functioning removals service. It should continue to say clearly that bookings, enquiries and payments are unavailable until the business is genuinely ready.

## 3. Images, rendering and responsiveness

### Image resolution
No HTML `<img>` elements were found in the reviewed pages. The prominent artwork is inline SVG and CSS decoration. SVG is resolution-independent, so it remains sharp on high-density phone and desktop screens. There are currently no photographic image files whose pixel dimensions or compression need correcting.

This is not a defect by itself. It does mean the website currently has an illustrated, concept-led feel rather than the proof and reassurance that genuine photographs of vehicles, packing work and staff can eventually provide. Only add real photos once the business has assets it can honestly represent. At that point use appropriately sized WebP/AVIF images, responsive variants and explicit dimensions to avoid layout shifts.

### Responsive source review
The stylesheet includes breakpoints around 1100px, 1000px, 900px, 720px and 380px, along with a mobile navigation mode and reduced-motion handling. The CSS also includes a visible keyboard-focus style and the pages include a skip-to-content link.

This confirms that responsive behaviour has been considered in the source. It does **not** prove that every viewport renders correctly. A real browser pass is still needed at narrow phone widths, larger phones, tablet widths, standard laptop widths and wide desktop screens. In particular, the many navigation links make the 720–900px transition worth checking visually.

### Rendering and performance
The static approach avoids a large framework runtime and does not require an application server to render ordinary pages. This is a good performance baseline, but no live Core Web Vitals, Lighthouse, real-device or cross-browser measurements were available in this source-only review. No performance score is claimed.

## 4. Code maintainability and security

### Shared page markup
The header, navigation, concept banner and footer are repeated across multiple HTML files. This is workable at the current scale, but a future navigation or wording change has to be made in several places. That creates a risk of pages drifting out of sync.

**Improvement path:** do not rewrite immediately. If page count and change frequency continue to grow, move the site to Astro using shared layouts and components. Astro can generate ordinary static HTML, so visitors do not need a large client-side application. This would reduce repetitive editing without requiring a React/Next.js application.

### CSS organisation
The stylesheet contains successive refinement sections and later rules that override earlier rules at the same or narrower breakpoints. Browsers resolve this correctly using CSS cascade rules, so the presence of overrides does not mean the site is broken. It does make future visual changes harder to reason about.

**Improvement path:** consolidate duplicate selectors only after recording current screenshots at key viewport sizes and comparing before/after. CSS cleanup without visual regression checks can unintentionally change spacing, layout or mobile behaviour. I have not altered the stylesheet.

### JavaScript
The shared script is small and focused. It handles:
- mobile menu open/close state;
- Escape key and outside-click behaviour;
- footer year;
- a local estimate calculation.

The current estimator uses a fixed set of form choices. Its displayed result is assembled with `innerHTML`; the values used today are constrained by the page's select options and fixed lookup tables, rather than free-form customer input. That is not an immediate exploit identified in this review, but changing the result rendering to DOM elements and `textContent` would be a more defensive pattern before introducing free-text fields or backend data.

The script does not currently submit customer details to a server. That is consistent with the stated concept-stage privacy position.

### Enquiry form
The form is disabled through a disabled `fieldset`, not merely a greyed-out button. That is the right safeguard for the current stage. Do not remove that safeguard until there is a secure endpoint, monitored mailbox, tested delivery, business-specific privacy notice and an approved operational process.

## 5. Search and content structure

The pages include page-specific titles, viewport metadata and canonical/social-sharing metadata in the reviewed content. The sitemap lists the principal customer-facing pages and the robots file points to it. The 404 page is marked `noindex` and is not listed in the sitemap.

One item to review later: the sitemap currently includes `quote.html`, although this is only an enquiry-form preview. That is not a functional error, but it may cause a search visitor to land on a page that cannot accept an enquiry. Consider excluding it from the sitemap and adding `noindex` when the search strategy is reviewed. This has not been changed because it affects search discovery.

## 6. Deployment and no-downtime design

The desired release process is:

1. Edit a separate development branch.
2. Run automatic checks for broken local links, missing pages, duplicate IDs, missing page metadata, images without alternative text, unsafe new-tab links, sitemap mistakes and the disabled enquiry-form safeguard.
3. Generate a preview deployment for review.
4. Check the preview on real phone, tablet and desktop browsers.
5. Approve the release.
6. Deploy the new version independently of the previous version, keeping rollback available.

Cloudflare Pages supports Git-connected preview deployments for custom branches and pull requests, with preview releases separate from production. That makes it a strong future fit for this static site, provided the account/project configuration is verified and deliberately approved. Its Git integration also needs its production branch controls configured correctly. No Cloudflare project, DNS or hosting setting was changed during this review.

A routine content release should not require a server outage. However, no provider can promise absolute zero downtime; independent previews, controlled production releases and rollback reduce the risk substantially.

## 7. Recommended target architecture

### Now
- Static HTML, CSS and JavaScript.
- Existing Git repository and custom domain arrangement.
- CDN-backed static hosting.
- No database, customer accounts or booking backend.
- Add automated repository quality checks.

### When enquiries are approved
- Add a separate server-side enquiry API.
- Validate data on the server; browser-side validation alone is not a security boundary.
- Store only the information actually needed to quote and perform a move.
- Use bot protection, rate limiting, access controls, encrypted storage, backups and tested deletion/retention.
- Send notifications through a transactional email provider.
- Complete the business-specific privacy notice and processor arrangements before collecting details.

### When bookings and payments are approved
- Add an availability/capacity service that prevents double-booking.
- Introduce quote acceptance, customer confirmations, cancellation/change handling and an administration view.
- Use a payment provider's hosted payment flow for deposits or balances; do not store card details.
- Keep the booking service deployable independently of the public website.

A small serverless API (for example, Cloudflare Workers) and managed database (for example, D1) could fit this architecture. That is a future design option, not an instruction to provision services now.

## 8. Priority list

| Priority | Action | Why |
|---|---|---|
| 1 | Add automated checks to every proposed change | Prevents simple regressions from reaching production |
| 2 | Run real browser tests at key screen widths | Source inspection cannot confirm rendering |
| 3 | Consolidate shared header/footer through templates when worthwhile | Reduces repeated manual edits |
| 4 | Consolidate CSS with screenshot comparisons | Reduces maintenance risk without accidental visual changes |
| 5 | Review whether the enquiry-preview page should be indexed | Avoids misleading search landings |
| 6 | Design and approve a secure enquiry backend | Required before collecting customer information |
| 7 | Build booking/payment only after operational readiness | Avoids unnecessary cost and risk before demand is proven |

## 9. What this review did not prove

- It did not confirm the live website's current HTTP response, TLS configuration, DNS health or hosting dashboard settings.
- It did not run Chrome, Safari, Firefox or physical-device screenshots.
- It did not measure Lighthouse scores or Core Web Vitals.
- It did not submit a live enquiry or payment, because those functions are intentionally disabled.
- It did not audit server logs, Cloudflare security events or GitHub account permissions.
- It did not validate every public market-price reference or the commercial viability of the draft price book.

Those are separate verification tasks. The next browser-based review should be completed against a preview deployment, not by changing the live site.

---

## Review conclusion

**Keep the current lightweight architecture. Do not migrate to React or Next.js.** Add repeatable quality checks now; consider Astro later if common page structure becomes costly to maintain. Keep the enquiry form disabled until business operations, privacy and secure data handling are ready.

The review and proposed checks are isolated from the production website. No public page or production setting has been changed.
