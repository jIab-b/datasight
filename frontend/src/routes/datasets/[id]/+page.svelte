<script lang="ts">
	export let params: { id: string }
	let ds: any = null
	const API = import.meta.env.VITE_API_URL || "http://localhost:8000"
	import { onMount } from 'svelte'
	onMount(async () => {
		const r = await fetch(`${API}/api/catalog/datasets/${params.id}`)
		ds = await r.json()
	})
</script>

{#if ds}
<h2>{ds.name}</h2>
<div>{ds.description}</div>
<h3>Fields</h3>
<ul>
	{#each ds.fields as f}
		<li>{f.name} ({f.dtype})</li>
	{/each}
</ul>
{:else}
<div>Loading</div>
{/if}
