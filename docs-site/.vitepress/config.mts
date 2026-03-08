import { defineConfig } from 'vitepress'
import { withMermaid } from "vitepress-plugin-mermaid"

export default withMermaid(defineConfig({
    title: "StepWright",
    description: "A declarative, step-by-step approach to web automation and data extraction with Playwright.",
    srcDir: './src',
    outDir: './dist',
    cleanUrls: true,
    lastUpdated: true,

    head: [
        ['link', { rel: 'icon', type: 'image/png', href: '/logo.png' }],
        ['meta', { name: 'theme-color', content: '#3eaf7c' }],
    ],

    themeConfig: {
        logo: '/logo.png',

        nav: [
            { text: 'Home', link: '/' },
            { text: 'Guide', link: '/guide/introduction' },
            { text: 'API Reference', link: '/api/reference' },
            { text: 'Changelog', link: '/changelog' }
        ],

        sidebar: {
            '/guide/': [
                {
                    text: 'Introduction',
                    items: [
                        { text: 'What is StepWright?', link: '/guide/introduction' },
                        { text: 'Installation', link: '/guide/installation' },
                        { text: 'Your First Scraper', link: '/guide/first-scraper' },
                        { text: 'Selectors & Data', link: '/guide/selectors-and-data' },
                        { text: 'Error Handling & Waits', link: '/guide/error-handling-and-waits' },
                        { text: 'Browser Options', link: '/guide/browser-options' },
                    ]
                },
                {
                    text: 'Advanced Features',
                    items: [
                        { text: 'Parallelism & Flow', link: '/guide/advanced/parallelism' },
                        { text: 'Data Flows', link: '/guide/advanced/data-flows' },
                        { text: 'Interactions', link: '/guide/advanced/interactions' },
                        { text: 'Pagination & Scrolling', link: '/guide/advanced/pagination' },
                        { text: 'Downloads & PDFs', link: '/guide/advanced/downloads-and-pdfs' },
                        { text: 'Navigating IFrames', link: '/guide/advanced/iframes' },
                    ]
                },
                {
                    text: 'Reference',
                    items: [
                        { text: 'Examples & Use Cases', link: '/guide/examples' },
                    ]
                }
            ],
            '/api/': [
                {
                    text: 'API Reference',
                    items: [
                        { text: 'Overview', link: '/api/reference' },
                        { text: 'Step Actions', link: '/api/actions' },
                    ]
                }
            ]
        },

        socialLinks: [
            { icon: 'github', link: 'https://github.com/lablnet/stepwright' }
        ],

        footer: {
            message: 'Released under the MIT License.',
            copyright: 'Copyright © 2026-present Muhammad Umer Farooq'
        },

        search: {
            provider: 'local'
        }
    },

    vite: {
        optimizeDeps: {
            include: [
                '@braintree/sanitize-url',
                'dayjs',
                'dayjs/plugin/customParseFormat.js',
                'dayjs/plugin/advancedFormat.js',
                'dayjs/plugin/isoWeek.js',
                'debug',
                'cytoscape-cose-bilkent',
                'cytoscape'
            ]
        },
        ssr: {
            noExternal: [
                'dayjs',
                '@braintree/sanitize-url',
                'debug',
                'cytoscape-cose-bilkent',
                'cytoscape'
            ]
        }
    }
}))
