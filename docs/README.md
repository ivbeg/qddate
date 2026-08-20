# qddate documentation

This directory contains the Docusaurus documentation site for qddate.

## Development

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
cd docs
npm install
```

### Local development

Start the development server:

```bash
npm start
```

This starts a local development server and opens a browser window. Most changes
are reflected live without restarting the server. From the repository root you
can also run `make docs-serve`.

### Build

Build the site for production:

```bash
npm run build
```

This generates static content into the `build` directory. From the repository
root you can also run `make docs`.

### Serve

Serve the built site locally:

```bash
npm run serve
```

## Project structure

```
docs/
├── docusaurus.config.js    # Docusaurus configuration
├── sidebars.js             # Sidebar navigation
├── package.json            # Node.js dependencies
├── babel.config.js         # Babel configuration
├── src/
│   ├── css/custom.css      # Custom styles
│   ├── pages/index.js      # Homepage (documentation contents)
│   └── components/         # React components
├── static/img/             # Logo and favicon
└── docs/                   # Documentation content
    ├── getting-started/    # Installation, quick start, cookbook
    ├── use-cases/          # End-to-end examples
    ├── api/                # Public Python API
    ├── languages/          # Pattern catalog by language
    ├── development/        # Contributing and internals
    └── license.md
```

Language pattern pages under `docs/languages/` (except `index.md`) are generated
by `scripts/generate_pattern_docs.py`. Do not edit them by hand.

## Deployment

The documentation is deployed to GitHub Pages at
[ivbeg.github.io/qddate](https://ivbeg.github.io/qddate/) when changes are
pushed to `master`. The workflow lives in `.github/workflows/deploy-docs.yml`.

### GitHub Pages setup

1. Open the repository settings on GitHub.
2. Navigate to **Pages**.
3. Under **Source**, select **GitHub Actions**.

See `GITHUB_PAGES_SETUP.md` for details.

## Documentation structure

- **Getting Started**: Installation, quick start, positioning, cookbook
- **Use Cases**: Scraping, bulk processing, news aggregation
- **API Reference**: `DateParser`, `parse`, `match`, `languages=`
- **Languages and Patterns**: Honest pattern catalog by language
- **Development**: Contributing, adding languages, community

## Contributing

When adding or updating documentation:

1. Edit the markdown files in `docs/docs/`.
2. Follow the existing frontmatter (`title`, `description`).
3. Test locally with `npm start`.
4. Confirm `npm run build` succeeds (broken links fail the build).
5. After changing date patterns, regenerate language pages with
   `python scripts/generate_pattern_docs.py`.
