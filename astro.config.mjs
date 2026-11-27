// @ts-check

import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
	site: 'https://qn51z.com',
	integrations: [
		mdx(),
		sitemap({
			// public/weaverlet/는 정적 파일이라 사이트맵에 자동으로 안 들어간다 (weaverlet-src/build.py와 같은 목록)
			customPages: ['', 'ko', 'ja', 'zh-hans', 'es', 'vi', 'ms', 'id', 'pt-br', 'th', 'ru', 'fr', 'de', 'it'].map(
				(l) => `https://qn51z.com/weaverlet/${l ? l + '/' : ''}`,
			),
		}),
	],
	redirects: {
		'/blog/weaverlet-making-of': '/blog/weaverlet/making-of/',
	},
});
