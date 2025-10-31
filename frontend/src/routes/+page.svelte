<script lang="ts">
	import DslInspector from "$lib/components/DslInspector.svelte"
	import ChartView from "$lib/components/ChartView.svelte"
	import DataGrid from "$lib/components/DataGrid.svelte"

	let dq = {
		DataQuery: {
			sources: [
				{
					dataset: "fact_price_daily",
					select: ["date", "region", "price_mwh"],
					where: { region: ["NSW", "QLD"] },
					time: { start: "2023-01-01", end: "2023-01-03", grain: "day" }
				},
				{
					dataset: "fact_demand_daily",
					select: ["date", "region", "demand_mw"],
					where: { region: ["NSW", "QLD"] },
					time: { start: "2023-01-01", end: "2023-01-03", grain: "day" }
				}
			],
			join: { on: ["date", "region"], how: "inner" },
			transforms: [
				{ op: "rolling_mean", field: "price_mwh", window: 2, as: "price_7d" }
			],
			limit_points: 5000,
			timezone: "UTC"
		},
		ChartSpec: {
			mark: "line",
			encoding: {
				x: { field: "date", type: "temporal" },
				y: [
					{ field: "demand_mw", type: "quantitative", axis: "left" },
					{ field: "price_7d", type: "quantitative", axis: "right" }
				],
				color: { field: "region", type: "nominal" }
			},
			title: "NSW vs QLD: Demand vs Price"
		}
	}
	let dqText = JSON.stringify(dq, null, 2)
	let rows: any[] = []
	let sql = ""
	let lastReceipt: string | null = null
	const API = import.meta.env.VITE_API_URL || "http://localhost:8000"

	async function preview() {
		const obj = JSON.parse(dqText)
		const r = await fetch(`${API}/api/query/preview`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(obj.DataQuery) })
		const j = await r.json()
		rows = j.rows
		sql = j.sql
	}
	async function run() {
		const obj = JSON.parse(dqText)
		const r = await fetch(`${API}/api/query/run`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(obj.DataQuery) })
		const j = await r.json()
		rows = j.rows
		sql = j.sql
		lastReceipt = j.receipt_id
	}
	async function save() {
		if (!lastReceipt) return
		const obj = JSON.parse(dqText)
		const r = await fetch(`${API}/api/charts/save`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ receipt_id: lastReceipt, chartspec: obj.ChartSpec, title: obj.ChartSpec.title }) })
		const j = await r.json()
		alert(`saved chart ${j.id}`)
	}
</script>

<section>
	<h2>DataQuery</h2>
	<DslInspector value={dqText} onChange={(v) => (dqText = v)} />
	<div style="display:flex;gap:8px;margin:8px 0;align-items:center">
		<button on:click={preview}>Preview</button>
		<button on:click={run}>Run</button>
		<button on:click={save} disabled={!lastReceipt}>Save</button>
	</div>
	<div><strong>SQL</strong></div>
	<pre>{sql}</pre>
</section>

<section>
	<h2>Chart</h2>
	{#if rows.length > 0}
		<ChartView rows={rows} spec={JSON.parse(dqText).ChartSpec} />
	{/if}
</section>

<section>
	<h2>Data</h2>
	<DataGrid {rows} />
</section>
