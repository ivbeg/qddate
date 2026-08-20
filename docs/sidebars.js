/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docs: [
    {
      type: 'link',
      label: 'Contents',
      href: '/',
    },
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quick-start',
        'getting-started/when-to-use',
        'getting-started/cookbook',
        'getting-started/basic-usage',
        'getting-started/performance',
        'getting-started/troubleshooting',
        'getting-started/best-practices',
      ],
    },
    {
      type: 'category',
      label: 'Use Cases',
      items: [
        'use-cases/web-scraping',
        'use-cases/bulk-processing',
        'use-cases/news-aggregation',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api/index',
        'api/dateparser',
        'api/parse',
        'api/match',
        'api/languages',
      ],
    },
    {
      type: 'category',
      label: 'Languages and Patterns',
      items: [
        'languages/index',
        'languages/en',
        'languages/bg',
        'languages/cz',
        'languages/de',
        'languages/es',
        'languages/fr',
        'languages/it',
        'languages/nl',
        'languages/pl',
        'languages/pt',
        'languages/ro',
        'languages/ru',
        'languages/tr',
        'languages/uk',
      ],
    },
    {
      type: 'category',
      label: 'Development',
      items: [
        'development/contributing',
        'development/adding-languages',
        'development/community',
      ],
    },
    'license',
  ],
};

module.exports = sidebars;
