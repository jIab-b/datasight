<script lang="ts">
	export let value: string
	export let onChange: (v: string) => void
	function handle(e: Event) {
		onChange && onChange((e.target as HTMLTextAreaElement).value)
	}
</script>

<textarea rows="14" style="width:100%" {value} on:input={handle}></textarea>
