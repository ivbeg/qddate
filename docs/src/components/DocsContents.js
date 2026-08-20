import React from 'react';
import Link from '@docusaurus/Link';
import styles from './DocsContents.module.css';

const sections = [
  {
    title: 'Getting Started',
    to: '/getting-started/installation',
    description: 'Install qddate and parse a first dirty date string in a few lines of Python.',
    links: [
      {label: 'Installation', to: '/getting-started/installation'},
      {label: 'Quick start', to: '/getting-started/quick-start'},
      {label: 'When to use', to: '/getting-started/when-to-use'},
      {label: 'Cookbook', to: '/getting-started/cookbook'},
      {label: 'Basic usage', to: '/getting-started/basic-usage'},
      {label: 'Performance', to: '/getting-started/performance'},
      {label: 'Troubleshooting', to: '/getting-started/troubleshooting'},
      {label: 'Best practices', to: '/getting-started/best-practices'},
    ],
  },
  {
    title: 'Use Cases',
    to: '/use-cases/web-scraping',
    description: 'End-to-end examples for scraping, bulk corpora, and news reconstruction.',
    links: [
      {label: 'Web scraping', to: '/use-cases/web-scraping'},
      {label: 'Bulk processing', to: '/use-cases/bulk-processing'},
      {label: 'News aggregation', to: '/use-cases/news-aggregation'},
    ],
  },
  {
    title: 'API Reference',
    to: '/api/',
    description: 'DateParser, parse, match, and the languages= constructor parameter.',
    links: [
      {label: 'API overview', to: '/api/'},
      {label: 'DateParser', to: '/api/dateparser'},
      {label: 'parse()', to: '/api/parse'},
      {label: 'match()', to: '/api/match'},
      {label: 'languages=', to: '/api/languages'},
    ],
  },
  {
    title: 'Languages and Patterns',
    to: '/languages/',
    description: 'Fourteen languages, 128+ base patterns, and generated time variants.',
    links: [
      {label: 'Language overview', to: '/languages/'},
      {label: 'English', to: '/languages/en'},
      {label: 'Russian', to: '/languages/ru'},
      {label: 'German', to: '/languages/de'},
      {label: 'Spanish', to: '/languages/es'},
      {label: 'Romanian', to: '/languages/ro'},
      {label: 'Ukrainian', to: '/languages/uk'},
    ],
  },
  {
    title: 'Development',
    to: '/development/contributing',
    description: 'Contributing, adding languages, community, and license.',
    links: [
      {label: 'Contributing', to: '/development/contributing'},
      {label: 'Adding languages', to: '/development/adding-languages'},
      {label: 'Community', to: '/development/community'},
      {label: 'License', to: '/license'},
    ],
  },
];

function Section({title, to, description, links}) {
  return (
    <article className={styles.card}>
      <h3 className={styles.cardTitle}>
        <Link to={to}>{title}</Link>
      </h3>
      <p className={styles.cardDescription}>{description}</p>
      <ul className={styles.linkList}>
        {links.map((item) => (
          <li key={item.label}>
            {item.href ? (
              <a href={item.href}>{item.label}</a>
            ) : (
              <Link to={item.to}>{item.label}</Link>
            )}
          </li>
        ))}
      </ul>
    </article>
  );
}

export default function DocsContents() {
  return (
    <section className={styles.contents}>
      <div className="container">
        <h2 className={styles.heading}>Documentation contents</h2>
        <p className={styles.intro}>
          Start with a section below, or use the sidebar from any page. The public
          entry point is <code>qddate.DateParser</code> and its <code>parse</code>{' '}
          method.
        </p>
        <div className={styles.grid}>
          {sections.map((section) => (
            <Section key={section.title} {...section} />
          ))}
        </div>
      </div>
    </section>
  );
}
