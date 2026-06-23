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
const generatedCandidates = computed(() => pipeline.current?.candidates || [])
const shortlist = computed(() => pipeline.current?.shortlist || [])
const assessmentQuestions = computed(() => {
  const assessment = pipeline.current?.assessments
  if (!assessment) return []
  return Array.isArray(assessment.questions) ? assessment.questions : []
})
const generatedInterviews = computed(() => pipeline.current?.interviews || [])
const generatedOffers = computed(() => pipeline.current?.offers || [])

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
    <section v-if="pipeline.current" class="pipeline-results" style="margin-top:24px">
      <article v-if="pipeline.current.jd_text" class="card generated-card">
        <div class="section-heading">
          <div>
            <h2>Generated Job Description</h2>
            <p class="muted">Posted references and approved description from the JD agent.</p>
          </div>
          <a v-if="pipeline.current.linkedin_job_url" class="button secondary" :href="pipeline.current.linkedin_job_url" target="_blank" rel="noreferrer">Open LinkedIn</a>
        </div>
        <dl class="result-meta">
          <div v-if="pipeline.current.greenhouse_job_id">
            <dt>Greenhouse ID</dt>
            <dd>{{ pipeline.current.greenhouse_job_id }}</dd>
          </div>
          <div v-if="pipeline.current.jd_validation_suggestions">
            <dt>Validation</dt>
            <dd>{{ pipeline.current.jd_validation_suggestions }}</dd>
          </div>
        </dl>
        <p class="generated-text">{{ pipeline.current.jd_text }}</p>
      </article>

      <article v-if="generatedCandidates.length" class="card generated-card">
        <div class="section-heading">
          <div>
            <h2>Candidate Screening</h2>
            <p class="muted">{{ shortlist.length }} shortlisted from {{ generatedCandidates.length }} screened candidates.</p>
          </div>
        </div>
        <div class="result-list">
          <div v-for="candidate in generatedCandidates" :key="candidate.id" class="result-row">
            <div>
              <strong>{{ candidate.full_name }}</strong>
              <p class="muted">{{ candidate.email }}</p>
              <p>{{ candidate.reasoning }}</p>
            </div>
            <span class="score-chip" :class="{ rejected: candidate.score < 60 }">{{ candidate.score }}</span>
          </div>
        </div>
      </article>

      <article v-if="pipeline.current.assessments" class="card generated-card">
        <div class="section-heading">
          <div>
            <h2>{{ pipeline.current.assessments.title || 'Assessment' }}</h2>
            <p class="muted">{{ pipeline.current.assessments.description || 'Generated assessment package.' }}</p>
          </div>
        </div>
        <ol v-if="assessmentQuestions.length" class="question-list">
          <li v-for="question in assessmentQuestions" :key="question">{{ question }}</li>
        </ol>
        <pre v-else class="mono result-json">{{ JSON.stringify(pipeline.current.assessments, null, 2) }}</pre>
      </article>

      <article v-if="generatedInterviews.length" class="card generated-card">
        <div class="section-heading">
          <div>
            <h2>Interview Plan</h2>
            <p class="muted">Scheduling links and generated question banks.</p>
          </div>
        </div>
        <div class="result-list">
          <div v-for="interview in generatedInterviews" :key="interview.candidate_id" class="result-row stacked">
            <div class="section-heading compact">
              <strong>{{ interview.candidate_id }}</strong>
              <a class="button secondary" :href="interview.calendly_link" target="_blank" rel="noreferrer">Open Link</a>
            </div>
            <ol class="question-list">
              <li v-for="question in interview.questions" :key="question">{{ question }}</li>
            </ol>
          </div>
        </div>
      </article>

      <article v-if="generatedOffers.length" class="card generated-card">
        <div class="section-heading">
          <div>
            <h2>Offer Drafts</h2>
            <p class="muted">Offer records created for selected candidates.</p>
          </div>
        </div>
        <div class="result-list">
          <div v-for="offer in generatedOffers" :key="offer.greenhouse_offer_id" class="result-row">
            <div>
              <strong>{{ offer.greenhouse_offer_id }}</strong>
              <p class="muted">{{ offer.candidate_id }}</p>
              <p>{{ offer.letter_preview }}</p>
            </div>
          </div>
        </div>
      </article>
    </section>
    <ApprovalModal v-if="showApproval" :state="pipeline.current" @approve="pipeline.approvePipeline(pipeline.current.job_id)" />
  </section>
</template>
