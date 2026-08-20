// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'qddate',
  tagline: 'Quick and dirty date parsing for scraped HTML',
  favicon: 'img/favicon.svg',

  url: 'https://ivbeg.github.io',
  baseUrl: '/qddate/',

  organizationName: 'ivbeg',
  projectName: 'qddate',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/ivbeg/qddate/edit/master/docs/docs/',
          routeBasePath: '/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/logo.svg',
      navbar: {
        title: 'qddate',
        logo: {
          alt: 'qddate logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            to: '/',
            label: 'Contents',
            position: 'left',
            activeBaseRegex: '^/qddate/?$',
          },
          {
            type: 'docSidebar',
            sidebarId: 'docs',
            position: 'left',
            label: 'Docs',
          },
          {
            to: '/getting-started/cookbook',
            label: 'Cookbook',
            position: 'left',
          },
          {
            href: 'https://ivbeg.github.io/qddate/llms.txt',
            label: 'llms.txt',
            position: 'right',
          },
          {
            href: 'https://github.com/ivbeg/qddate',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Contents',
                to: '/',
              },
              {
                label: 'Getting Started',
                to: '/getting-started/installation',
              },
              {
                label: 'API Reference',
                to: '/api/',
              },
              {
                label: 'Languages',
                to: '/languages/',
              },
              {
                label: 'Cookbook',
                to: '/getting-started/cookbook',
              },
            ],
          },
          {
            title: 'For coding agents',
            items: [
              {
                label: 'llms.txt',
                href: 'https://ivbeg.github.io/qddate/llms.txt',
              },
              {
                label: 'API overview',
                to: '/api/',
              },
              {
                label: 'Pattern catalog',
                to: '/languages/',
              },
              {
                label: 'Adding languages',
                to: '/development/adding-languages',
              },
            ],
          },
          {
            title: 'Project',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/ivbeg/qddate',
              },
              {
                label: 'PyPI',
                href: 'https://pypi.org/project/qddate/',
              },
              {
                label: 'Changelog',
                href: 'https://github.com/ivbeg/qddate/blob/master/CHANGELOG.md',
              },
              {
                label: 'License',
                to: '/license',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Ivan Begtin and contributors. qddate is BSD licensed.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['python', 'bash', 'yaml', 'json'],
      },
    }),
};

module.exports = config;
