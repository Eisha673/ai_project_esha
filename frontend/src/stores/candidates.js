import { defineStore } from 'pinia'
import api from '../api'

export const useCandidatesStore = defineStore('candidates', {
  state: () => ({ candidates: [] }),
  actions: {
    async fetchCandidates(jobId) {
      const { data } = await api.get('/candidates', { params: jobId ? { job_id: jobId } : {} })
      this.candidates = data
    },
  },
})
