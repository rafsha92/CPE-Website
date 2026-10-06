# CPE Patch website

A bilingual static website for Malaysian commercial premises, following the approved eleven-section design and scrolling effects. Bahasa Melayu is the default, with equivalent English pages.

Published address: https://rafsha92.github.io/CPE-Website/

## Editing

- Content and page templates: `tools/build-site.py`
- Layout, typography and fallback motion: `src/assets/site.css`
- GSAP scrolling effects, interactions and enquiry form: `src/assets/site.js`
- Images, local Manrope font and GSAP libraries: `src/assets/`
- Motion specification: `SCROLLING-EFFECTS.md`

All build commands use Python 3. No third-party Python packages are needed. The build copies assets into `dist/` and generates 20 language pages, the Malay homepage alias, the error page, sitemap and robots file. Generated output is ignored by Git.

```sh
python tools/build-site.py --origin https://rafsha92.github.io/CPE-Website
python tools/check-site.py --origin https://rafsha92.github.io/CPE-Website
python tools/serve.py --port 8741 --base-path /CPE-Website
```

Preview: http://127.0.0.1:8741/CPE-Website/ms/

The full site URL controls both the hosting path and SEO URLs. To use another domain, rebuild with that domain as `--origin`; root hosting works without a path. CSS assets use relative paths. Canonical, alternate language, Open Graph and sitemap URLs are generated together. Styles and scripts have content hashes to refresh changed assets.

## Publishing

`.github/workflows/pages.yml` builds and checks the website before deploying `dist/` through GitHub Pages. A push to `main` publishes automatically. You can also run **Publish CPE website** manually from the repository's Actions tab.

The repository's Pages publishing source must be **GitHub Actions**. The workflow reads the actual Pages address at build time, so changing to an approved custom domain also updates generated links and SEO metadata on the next deployment.

## Contact and content

The contact details from the supplied brochure are configured in the page builder. The form validates entries and prepares a WhatsApp message for the visitor to review and send. There is no enquiry database, automatic message sending or analytics integration.

Only CPE branding and the generic CPE team label appear on the website. Photographs are marked as illustrative. The brochure's shop example is labelled and distinguishes compressor savings from total bill changes. Unconfirmed commercial terms are excluded; proposals are discussed with the CPE team.

GSAP 3.15.0 and ScrollTrigger are served locally with their original license notices. Download sources and hashes are recorded in `tools/vendor-sources.json`. Manrope includes its OFL license. The site respects reduced motion and keeps its content available without JavaScript.
