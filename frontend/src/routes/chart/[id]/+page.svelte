<script lang="ts">
	export let params: { id: string }
	let chart: any = null
	let rows: any[] = []
	const API = import.meta.env.VITE_API_URL || "http://localhost:8000"
	import { onMount } from 'svelte'
	async function loadCsv(url: string) {
		const r = await fetch(url)
		const text = await r.text()
		const [h, ...rest] = text.trim().split("\n")
		const headers = h.split(",")
		return rest.map((line) => {
			const cols = line.split(",")
			const obj: any = {}
			headers.forEach((k, i) => (obj[k] = cols[i]))
			return obj
		})
	}
	onMount(async () => {
		const r = await fetch(`${API}/api/charts/${params.id}`)
		chart = await r.json()
		if (chart && chart.receipt_id) rows = await loadCsv(`${API}/api/export/csv?receipt=${chart.receipt_id}`)
	})
</script>

{#if chart}
<h2>{chart.title}</h2>
<pre>{JSON.stringify(chart.chartspec, null, 2)}</pre>
{:else}
<div>Loading</div>
{/if}
