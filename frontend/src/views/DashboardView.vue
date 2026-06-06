<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const kpis = ref([
  ['Active Jobs', 0, 'work_outline'],
  ['Candidates in Pipeline', 0, 'group'],
  ['Interviews Scheduled', 0, 'calendar_today'],
  ['Offers Sent', 0, 'description'],
])
const activity = ref([])

onMounted(async () => {
  const [jobs, candidates, interviews, offers, recent] = await Promise.allSettled([
    api.get('/jobs'),
    api.get('/candidates'),
    api.get('/interviews'),
    api.get('/offers'),
    api.get('/pipeline/activity/recent'),
  ])
  kpis.value[0][1] = jobs.value?.data?.length || 0
  kpis.value[1][1] = candidates.value?.data?.length || 0
  kpis.value[2][1] = interviews.value?.data?.length || 0
  kpis.value[3][1] = offers.value?.data?.length || 0
  activity.value = recent.value?.data || []
})
</script>

<template>
  <section>
    <div style="display:flex;justify-content:space-between;gap:16px;align-items:end;margin-bottom:24px">
      <div>
        <h1 class="page-title">Dashboard Overview</h1>
        <p class="muted">Real-time status of your AI-driven recruitment lifecycle.</p>
      </div>
      <RouterLink class="button" to="/jobs" style="text-decoration:none">Start New Pipeline</RouterLink>
    </div>
    <div class="grid kpis">
      <article v-for="[label, value, icon] in kpis" :key="label" class="card">
        <span class="material-symbols-outlined" style="color:#4f46e5">{{ icon }}</span>
        <p class="muted" style="font-size:12px;font-weight:800;text-transform:uppercase">{{ label }}</p>
        <strong style="font-size:32px">{{ value }}</strong>
      </article>
    </div>
    <section class="card" style="margin-top:24px">
      <h2 style="margin-top:0">Recent AI Activity</h2>
      <div v-for="item in activity" :key="`${item.agent_name}-${item.created_at}`" style="border-top:1px solid #e2e8f0;padding:12px 0">
        <strong>{{ item.agent_name }}</strong>
        <span class="muted"> using {{ item.nim_model || item.llm_provider }}</span>
        <p style="margin:4px 0 0">{{ item.output_summary }}</p>
      </div>
    </section>
  </section>
</template>
