export const SITE_TITLE = 'JISUB KIM BLOG';
export const SITE_DESCRIPTION = '직접 부딪힌 개발 문제와 해결 과정을 기록합니다.';

export type Lang = 'ko' | 'en';

export const UI = {
	ko: {
		description: SITE_DESCRIPTION,
		home: '/',
		about: '소개',
		privacy: '개인정보처리방침',
		contact: '문의',
		switchLabel: 'EN',
		updated: 'Last updated on',
	},
	en: {
		description: 'Notes on development problems I ran into and how I solved them.',
		home: '/en/',
		about: 'About',
		privacy: 'Privacy Policy',
		contact: 'Contact',
		switchLabel: '한국어',
		updated: 'Last updated on',
	},
} as const;

export const prefix = (lang: Lang): string => (lang === 'en' ? '/en' : '');
