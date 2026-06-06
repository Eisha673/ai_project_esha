<script setup>
defineProps({
  score: { type: Number, default: null },
  biasFlag: { type: Boolean, default: false },
})

const colorFor = (score) => {
  if (score === null || score === undefined) return '#64748b'
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#f59e0b'
  return '#f43f5e'
}
</script>

<template>
  <span class="badge" :style="{ background: colorFor(score), color: '#fff', display: 'inline-flex', alignItems: 'center', gap: '6px' }">
    <span>{{ score ?? '--' }}</span>
    <span>Nemotron</span>
    <span v-if="biasFlag" class="material-symbols-outlined" title="Bias flag detected" style="font-size:16px;color:#fff3cd">warning</span>
  </span>
</template>
