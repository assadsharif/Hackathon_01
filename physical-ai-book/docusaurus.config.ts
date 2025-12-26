import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Physical AI & Humanoid Robotics Book',
  tagline: 'A comprehensive guide to embodied intelligence and humanoid robotics',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://assadsharif.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/Hackathon_01/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'assadsharif', // Usually your GitHub org/user name.
  projectName: 'Hackathon_01', // Usually your repo name.

  onBrokenLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  // Custom fields for application configuration
  customFields: {
    // RAG Chatbot API URL - set via environment variable or use local default
    chatbotApiUrl: process.env.CHATBOT_API_URL || 'http://localhost:8000/v1',
  },

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',
          sidebarPath: './sidebars.ts',
          // Edit this page link points to the physical-ai-book docs folder in the repo
          editUrl:
            'https://github.com/assadsharif/Hackathon_01/tree/main/physical-ai-book/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    // Algolia DocSearch configuration
    // Apply for free DocSearch at: https://docsearch.algolia.com/apply/
    // After approval, replace the placeholder values below with your actual credentials
    algolia: {
      appId: 'YOUR_APP_ID', // Provided by Algolia after approval
      apiKey: 'YOUR_SEARCH_API_KEY', // Public search-only API key
      indexName: 'physical-ai-book', // Index name (you choose this when applying)

      // Optional: See doc section below
      contextualSearch: true,

      // Optional: Specify domains where the search should work
      // searchParameters: {},

      // Optional: Path for search page that is enabled by default (`false` to disable it)
      searchPagePath: 'search',
    },
    navbar: {
      title: 'Physical AI Book',
      items: [
        {
          href: 'https://github.com/assadsharif/Hackathon_01',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Content',
          items: [
            {
              label: 'Curriculum Overview',
              to: '/',
            },
          ],
        },
        {
          title: 'Repository',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/assadsharif/Hackathon_01',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI Book Project. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
