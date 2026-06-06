<script setup>
defineProps({
  state: { type: Object, required: true },
})
defineEmits(['approve'])
</script>

<template>
  <div style="position:fixed;inset:0;background:rgba(15,23,42,.35);display:grid;place-items:center;z-index:10">
    <section class="card" style="width:min(680px,calc(100vw - 32px));border-top:8px solid #f59e0b">
      <h2 style="margin-top:0">Human Approval Required</h2>
      <p class="muted">Review the current agent output before the pipeline dispatches the next QStash job.</p>
      <pre class="mono" style="white-space:pre-wrap;background:#f8fafc;border:1px solid #e2e8f0;padding:12px;border-radius:6px;max-height:320px;overflow:auto">{{ JSON.stringify(state, null, 2) }}</pre>
      <div style="display:flex;justify-content:flex-end;gap:12px;margin-top:16px">
        <button class="button secondary">Request Agent Re-run</button>
        <button class="button" @click="$emit('approve')">Approve for Next Stage</button>
      </div>
    </section>
  </div>
</template>
