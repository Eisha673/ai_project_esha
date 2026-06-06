<script setup>
defineProps({
  state: { type: Object, default: null },
})
</script>

<template>
  <div class="card">
    <h3 style="margin-top:0">Pipeline Timeline</h3>
    <pre class="mono" style="white-space:pre-wrap;margin-bottom:0">{{ JSON.stringify(state || {}, null, 2) }}</pre>
  </div>
</template>
