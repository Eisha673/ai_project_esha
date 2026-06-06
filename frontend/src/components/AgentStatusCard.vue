<script setup>
const props = defineProps({
  agentName: { type: String, required: true },
  modelName: { type: String, required: true },
  status: { type: String, default: 'Waiting' },
  errorMessage: { type: String, default: '' },
})

const styles = {
  Waiting: ['#f1f5f9', '#64748b'],
  Running: ['#dbeafe', '#2563eb'],
  Done: ['#dcfce7', '#16a34a'],
  Failed: ['#fee2e2', '#dc2626'],
}
</script>

<template>
  <article class="card" :style="{ borderLeft: `4px solid ${styles[props.status]?.[1] || '#64748b'}` }">
    <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start">
      <div>
        <h3 style="margin:0 0 4px">{{ agentName }}</h3>
        <p class="muted" style="margin:0;font-size:12px">{{ modelName }}</p>
      </div>
      <span class="badge" :style="{ background: styles[props.status]?.[0], color: styles[props.status]?.[1] }">
        {{ status }}
      </span>
    </div>
    <p v-if="errorMessage" style="color:#ba1a1a;margin-bottom:0">{{ errorMessage }}</p>
    <footer class="muted" style="margin-top:16px;font-size:12px">NIM Safety Guard enforced</footer>
  </article>
</template>
