<script lang="ts">
	import Plotly from 'plotly.js-dist-min'
	export let rows: any[] = []
	export let spec: any
	let el: HTMLDivElement
	function render() {
		if (!rows || rows.length === 0 || !spec) return
		const enc = spec.encoding || {}
		const xField = enc.x?.field
		let yFields: string[] = []
		if (Array.isArray(enc.y)) yFields = enc.y.map((c: any) => c.field)
		else if (enc.y?.field) yFields = [enc.y.field]
		const colorField = enc.color?.field
		const groups = new Map<string, any[]>()
		for (const r of rows) {
			const key = colorField ? String(r[colorField]) : "__all__"
			if (!groups.has(key)) groups.set(key, [])
			groups.get(key)!.push(r)
		}
		const traces: any[] = []
		for (const [g, arr] of groups.entries()) {
			const x = arr.map((r) => r[xField])
			if (yFields.length === 0) continue
			traces.push({ x, y: arr.map((r) => r[yFields[0]]), type: spec.mark === 'scatter' ? 'scatter' : 'scatter', mode: 'lines', name: g === "__all__" ? undefined : g })
			if (yFields.length > 1) traces.push({ x, y: arr.map((r) => r[yFields[1]]), type: 'scatter', mode: 'lines', name: (g === "__all__" ? '' : g + ' ') + yFields[1], yaxis: 'y2' })
		}
		const layout: any = { title: spec.title || '', xaxis: { title: xField } }
		if (yFields.length > 1) layout.yaxis2 = { overlaying: 'y', side: 'right' }
		Plotly.react(el, traces, layout, { responsive: true })
	}
	$: render()
</script>

<div bind:this={el} style="width:100%;height:420px"></div>
