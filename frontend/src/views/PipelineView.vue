<script setup>
import { computed, onBeforeUnmount, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AgentStatusCard from '../components/AgentStatusCard.vue'
import ApprovalModal from '../components/ApprovalModal.vue'
import PipelineTimeline from '../components/PipelineTimeline.vue'
import { usePipelineStore } from '../stores/pipeline'

const route = useRoute()
const pipeline = usePipelineStore()

const agents = [
  ['JD Agent', 'Claude Sonnet 4 + NIM Safety Guard', 'jd'],
  ['Search Agent', 'NVIDIA Nemotron Super 49B', 'search'],
  ['Assessment Agent', 'Mistral-Nemotron', 'assessment'],
  ['Interview Agent', 'GPT-4o + Calendly', 'interview'],
  ['Offer Agent', 'Claude Sonnet 4 + NIM Safety Guard', 'offer'],
]

const statusFor = (stage) => {
  if (!pipeline.current) return 'Waiting'
  if (pipeline.current.errors?.length) return stage === pipeline.current.current_stage ? 'Failed' : 'Waiting'
  const order = ['jd', 'search', 'assessment', 'interview', 'offer', 'complete']
  const current = order.indexOf(pipeline.current.current_stage)
  const mine = order.indexOf(stage)
  if (pipeline.current.current_stage === 'complete' || mine < current) return 'Done'
  if (mine === current) return pipeline.current.human_approved === false ? 'Done' : 'Running'
  return 'Waiting'
}

const showApproval = computed(() => pipeline.current && pipeline.current.human_approved === false && !pipeline.current.errors?.length)

onMounted(() => {
  if (route.params.jobId) pipeline.pollStatus(route.params.jobId)
})
onBeforeUnmount(pipeline.stopPolling)
</script>

<template>
  <section>
    <h1 class="page-title">Pipeline</h1>
    <p class="muted">Agents advance through QStash jobs and pause at human approval gates.</p>
    <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(220px,1fr));margin-top:24px">
      <AgentStatusCard v-for="[name, model, stage] in agents" :key="stage" :agent-name="name" :model-name="model" :status="statusFor(stage)" :error-message="pipeline.current?.errors?.[0] || ''" />
    </div>
    <section v-if="pipeline.current?.errors?.length" class="card" style="margin-top:24px;border-color:#ba1a1a;color:#ba1a1a">
      {{ pipeline.current.errors.join('\n') }}
    </section>
    <PipelineTimeline style="margin-top:24px" :state="pipeline.current" />
    <ApprovalModal v-if="showApproval" :state="pipeline.current" @approve="pipeline.approvePipeline(pipeline.current.job_id)" />
  </section>
</template>
