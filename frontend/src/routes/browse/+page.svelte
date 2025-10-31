<script lang="ts">
	let datasets: any[] = []
	const API = import.meta.env.VITE_API_URL || "http://localhost:8000"
	onMount(async () => {
		const r = await fetch(`${API}/api/catalog/datasets`)
		datasets = await r.json()
	})
	import { onMount } from 'svelte'
</script>

<h2>Datasets</h2>
<ul>
	{#each datasets as d}
		<li><a href={`/datasets/${encodeURIComponent(d.id)}`}>{d.name} ({d.id})</a></li>
	{/each}
</ul>
