import { readFileSync } from "fs";
import { timeFormat } from "d3";
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import path from "path";
import { enhancedImages } from '@sveltejs/enhanced-img';
import dsv from "@rollup/plugin-dsv";
import type { Plugin } from 'vite';

const { version } = JSON.parse(readFileSync("package.json", "utf8"));
const timestamp = timeFormat("%Y-%m-%d-%H:%M")(new Date());

// Custom plugin to ensure DSV handles CSV files in all build contexts
function dsvPlugin(): Plugin {
	const dsvInstance = dsv();
	return {
		name: 'vite-plugin-dsv-all-contexts',
		enforce: 'pre',
		...dsvInstance
	};
}

export default defineConfig({
	define: {
		__VERSION__: JSON.stringify(version),
		__TIMESTAMP__: JSON.stringify(timestamp)
	},
	plugins: [dsvPlugin(), enhancedImages(), sveltekit()],
	resolve: {
		alias: {
			$data: path.resolve("./src/data"),
			$styles: path.resolve("./src/styles"),
		}
	},
	optimizeDeps: {
		exclude: ['@duckdb/duckdb-wasm'],
	},
	ssr: {
		noExternal: ['d3-regression']
	},
	worker: {
		format: 'es'
	}
});
