# Movers4Less website

Premium, responsive single-page website for Movers4Less, focused on generating quotation enquiries for moves in London and surrounding areas.

## Files

- `index.html` — page structure, SEO metadata and service content
- `styles.css` — responsive visual design
- `script.js` — mobile navigation, date handling and quote form behaviour
- `favicon.svg` — browser icon
- `CNAME` — existing custom domain (unchanged)

## Before publishing

The design and quote form UI are prepared, but the form is **not live yet**. Complete these items before merging to the production branch:

1. Confirm the business enquiry email and add it to `MOVERS4LESS_CONFIG.quoteEmail` in `script.js`.
2. Choose the preferred form delivery method. The current starter implementation opens the visitor's email application (mailto); for reliable submissions from mobile and desktop, connect a form service or serverless endpoint and test it end to end.
3. Add a genuine business telephone number / WhatsApp link if customers should be able to call or message directly.
4. Confirm the exact services offered, coverage boundaries and any claims about insurance, packing, storage, licences or credentials before adding them.
5. Add a privacy notice and link it from the footer before collecting customer information. Confirm the data controller, lawful basis, retention period and any third-party processors.
6. Test the quote journey, keyboard access, mobile layout, page speed and domain HTTPS.

## Publishing

The work is on the `website-redesign` branch. Review and merge it into `main` only after the launch items above have been completed. The existing custom domain file has not been changed.
