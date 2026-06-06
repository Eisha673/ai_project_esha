import { defineStore } from 'pinia'
import api from '../api'

export const usePipelineStore = defineStore('pipeline', {
  state: () => ({
    current: null,
    pollingId: null,
    loading: false,
    error: null,
  }),
  actions: {
    async startPipeline(payload) {
      this.loading = true
      try {
        const { data } = await api.post('/pipeline/start', payload)
        await this.pollStatus(data.job_id)
        return data
      } finally {
        this.loading = false
      }
    },
    async pollStatus(jobId) {
      this.stopPolling()
      const load = async () => {
        const { data } = await api.get(`/pipeline/${jobId}/status`)
        this.current = data
      }
      await load()
      this.pollingId = setInterval(load, 3000)
    },
    async approvePipeline(jobId) {
      const { data } = await api.post(`/pipeline/${jobId}/approve`)
      await this.pollStatus(jobId)
      return data
    },
    stopPolling() {
      if (this.pollingId) clearInterval(this.pollingId)
      this.pollingId = null
    },
  },
})
