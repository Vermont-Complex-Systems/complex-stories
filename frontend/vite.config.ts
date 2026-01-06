import { readFileSync } from "fs";
import { timeFormat } from "d3";
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import path from "path";
import { enhancedImages } from '@sveltejs/enhanced-img';
import dsv from "@rollup/plugin-dsv";


process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';


const { version } = JSON.parse(readFileSync("package.json", "utf8"));
const timestamp = timeFormat("%Y-%m-%d-%H:%M")(new Date());

export default defineConfig({
	define: {
		__VERSION__: JSON.stringify(version),
		__TIMESTAMP__: JSON.stringify(timestamp)
	},
	plugins: [dsv(), enhancedImages(), sveltekit()],
	resolve: {
		alias: {
			$data: path.resolve("./src/data"),
			$styles: path.resolve("./src/styles"),
			$stories: path.resolve("./src/lib/stories"),
		}
	},
	ssr: {
		noExternal: ['d3-regression']
	},
	worker: {
		format: 'es'
	}
});
