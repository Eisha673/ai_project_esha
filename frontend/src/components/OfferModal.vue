<script setup>
defineProps({
  offer: { type: Object, default: null },
})
defineEmits(['close'])
</script>

<template>
  <div v-if="offer" style="position:fixed;inset:0;background:rgba(15,23,42,.35);display:grid;place-items:center;z-index:10">
    <section class="card" style="width:min(620px,calc(100vw - 32px))">
      <button class="button secondary" style="float:right" @click="$emit('close')">Close</button>
      <h2>Offer</h2>
      <pre class="mono" style="white-space:pre-wrap">{{ JSON.stringify(offer, null, 2) }}</pre>
    </section>
  </div>
</template>
