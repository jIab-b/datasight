<script lang="ts">
	export let rows: any[] = []
	const headers = rows && rows[0] ? Object.keys(rows[0]) : []
</script>

{#if rows && rows.length > 0}
<table>
	<thead>
		<tr>
			{#each headers as h}
				<th>{h}</th>
			{/each}
		</tr>
	</thead>
	<tbody>
		{#each rows as r}
			<tr>
				{#each headers as h}
					<td>{r[h]}</td>
				{/each}
			</tr>
		{/each}
	</tbody>
</table>
{:else}
<div>No data</div>
{/if}
