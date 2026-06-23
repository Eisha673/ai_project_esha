<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useJobsStore } from '../stores/jobs'
import { usePipelineStore } from '../stores/pipeline'

const router = useRouter()
const jobs = useJobsStore()
const pipeline = usePipelineStore()
const form = reactive({ title: '', department: '', seniority: '', notes: '', skills: '', location: 'Remote' })
const error = ref('')

onMounted(jobs.fetchJobs)

const submit = async () => {
  error.value = ''
  try {
    const result = await pipeline.startPipeline({ ...form, skills: form.skills.split(',').map(s => s.trim()).filter(Boolean) })
    await jobs.fetchJobs()
    router.push(`/pipeline/${result.job_id}`)
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Could not start pipeline'
  }
}

const openJob = (jobId) => {
  router.push(`/pipeline/${jobId}`)
}
</script>

<template>
  <section>
    <h1 class="page-title">Jobs</h1>
    <form class="card grid" style="max-width:760px;margin:24px 0" @submit.prevent="submit">
      <input v-model="form.title" class="input" required placeholder="Role title" />
      <input v-model="form.department" class="input" placeholder="Department" />
      <input v-model="form.seniority" class="input" placeholder="Seniority" />
      <input v-model="form.skills" class="input" placeholder="Skills, comma separated" />
      <textarea v-model="form.notes" class="input" placeholder="Notes"></textarea>
      <p v-if="error" style="margin:0;color:#ba1a1a;font-weight:700">{{ error }}</p>
      <button class="button" :disabled="pipeline.loading">{{ pipeline.loading ? 'Starting...' : 'Start New Pipeline' }}</button>
    </form>
    <div class="grid">
      <article
        v-for="job in jobs.jobs"
        :key="job.id"
        class="card job-card"
        role="button"
        tabindex="0"
        @click="openJob(job.id)"
        @keydown.enter.prevent="openJob(job.id)"
        @keydown.space.prevent="openJob(job.id)"
      >
        <div class="section-heading compact">
          <div>
            <strong>{{ job.title }}</strong>
            <p class="muted">{{ job.department || 'No department' }} - {{ job.status }}</p>
          </div>
          <RouterLink class="button secondary" :to="`/pipeline/${job.id}`" @click.stop>Open Pipeline</RouterLink>
        </div>
        <p v-if="job.jd_text" class="generated-text" style="margin-top:14px">{{ job.jd_text.slice(0, 260) }}{{ job.jd_text.length > 260 ? '...' : '' }}</p>
        <a v-if="job.linkedin_job_url" :href="job.linkedin_job_url" target="_blank" rel="noreferrer" class="muted" style="display:inline-block;margin-top:10px">LinkedIn posting</a>
      </article>
    </div>
  </section>
</template>
