import { error, redirect } from '@sveltejs/kit';
import storiesData from '$data/stories.csv';

// Vite analyzes these globs at build time — no runtime dynamic import needed
const storyModules = import.meta.glob('/src/lib/stories/*/components/Index.svelte');
const copyModules = import.meta.glob('/src/lib/stories/*/data/copy.json');

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function formatMonth(dateStr: string): string {
	const [month, , year] = dateStr.split('/').map(Number);
	return `${MONTHS[month - 1]} ${year}`;
}

function parseTags(tags: string): string[] {
	if (!tags) return [];
	return tags
		.split(',')
		.map((t: string) => t.trim())
		.filter(Boolean);
}

export async function load({ params }: { params: { slug: string } }) {
	const { slug } = params;

	// Resolve story metadata
	const storyRaw = (storiesData as any[]).find((d: any) => d.slug === slug);
	if (!storyRaw) error(404, 'Story not found');
	if (storyRaw.externalUrl) redirect(302, storyRaw.externalUrl);

	const story = {
		...storyRaw,
		month: formatMonth(storyRaw.date),
		tags: parseTags(storyRaw.tags)
	};

	// Resolve component (static glob — Vite bundles all story components at build time)
	const componentPath = `/src/lib/stories/${slug}/components/Index.svelte`;
	if (!(componentPath in storyModules)) error(404, `Story "${slug}" not found`);
	const mod = await (storyModules[componentPath] as () => Promise<{ default: any }>)();

	// Resolve copy data (static glob — same approach)
	let copyData: any = {};
	const copyPath = `/src/lib/stories/${slug}/data/copy.json`;
	if (copyPath in copyModules) {
		const copyMod = await (copyModules[copyPath] as () => Promise<any>)();
		copyData = copyMod.default || copyMod;
	}

	return { component: mod.default, story, copyData };
}
