// @ts-check

import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
	site: 'https://qn51z.com',
	integrations: [mdx(), sitemap()],
	redirects: {
		'/blog/weaverlet-making-of': '/blog/weaverlet/making-of/',
	},
});
