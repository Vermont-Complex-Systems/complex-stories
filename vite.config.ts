import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import path from "path";
import { enhancedImages } from '@sveltejs/enhanced-img';
import dsv from "@rollup/plugin-dsv";

export default defineConfig({
	plugins: [enhancedImages(), sveltekit(), dsv()],
	resolve: {
		alias: {
			$data: path.resolve("./src/data"),
			$styles: path.resolve("./src/styles"),
		}
	}
});
