import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			fallback: '404.html'
		}),
		paths: {
			base: process.argv.includes('dev') ? '' : process.env.BASE_PATH
		},
		prerender: {
			handleHttpError: ({ path, referrer, message }) => {
				console.warn(`Skipping ${path}: ${message}`);

			}
		}
	}
};

export default config;