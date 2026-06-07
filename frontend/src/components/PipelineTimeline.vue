<script setup>
import { computed } from 'vue'

const stages = [
  ['jd', 'JD', 'Role brief and job description'],
  ['search', 'Search', 'Candidate screening'],
  ['assessment', 'Assessment', 'Skills evaluation'],
  ['interview', 'Interview', 'Interview scheduling'],
  ['offer', 'Offer', 'Offer creation'],
  ['complete', 'Complete', 'Pipeline finished'],
]

const props = defineProps({
  state: { type: Object, default: null },
})

const currentIndex = computed(() => {
  const current = props.state?.current_stage || 'jd'
  const index = stages.findIndex(([stage]) => stage === current)
  return index === -1 ? 0 : index
})

const statusFor = (index) => {
  if (props.state?.errors?.length) return index === currentIndex.value ? 'Failed' : 'Waiting'
  if (index < currentIndex.value) return 'Done'
  if (index === currentIndex.value) return props.state?.human_approved === false ? 'Approval' : 'Running'
  return 'Waiting'
}
</script>

<template>
  <div class="card">
    <h3 style="margin-top:0">Pipeline Timeline</h3>
    <div v-if="state" style="display:grid;gap:12px">
      <div v-for="([stage, label, description], index) in stages" :key="stage" style="display:grid;grid-template-columns:28px 1fr auto;gap:12px;align-items:center">
        <span
          style="width:28px;height:28px;border-radius:999px;display:grid;place-items:center;font-size:13px;font-weight:900"
          :style="{ background: index <= currentIndex ? '#4f46e5' : '#e2e8f0', color: index <= currentIndex ? 'white' : '#64748b' }"
        >
          {{ index + 1 }}
        </span>
        <div>
          <strong>{{ label }}</strong>
          <p class="muted" style="margin:2px 0 0">{{ description }}</p>
        </div>
        <span style="font-size:12px;font-weight:800;text-transform:uppercase" :style="{ color: statusFor(index) === 'Failed' ? '#ba1a1a' : '#4f46e5' }">
          {{ statusFor(index) }}
        </span>
      </div>
      <section v-if="state.jd_text" style="border-top:1px solid #e2e8f0;margin-top:4px;padding-top:12px">
        <strong>Generated JD</strong>
        <p style="margin:6px 0 0">{{ state.jd_text }}</p>
      </section>
    </div>
    <p v-else class="muted" style="margin-bottom:0">No pipeline selected.</p>
  </div>
</template>
