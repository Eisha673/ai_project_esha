<script setup>
import { onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useJobsStore } from '../stores/jobs'
import { usePipelineStore } from '../stores/pipeline'

const router = useRouter()
const jobs = useJobsStore()
const pipeline = usePipelineStore()
const form = reactive({ title: '', department: '', seniority: '', notes: '', skills: '', location: 'Remote' })

onMounted(jobs.fetchJobs)

const submit = async () => {
  const result = await pipeline.startPipeline({ ...form, skills: form.skills.split(',').map(s => s.trim()).filter(Boolean) })
  router.push(`/pipeline/${result.job_id}`)
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
      <button class="button">Start New Pipeline</button>
    </form>
    <div class="grid">
      <article v-for="job in jobs.jobs" :key="job.id" class="card">
        <strong>{{ job.title }}</strong>
        <p class="muted">{{ job.department }} · {{ job.status }}</p>
      </article>
    </div>
  </section>
</template>
