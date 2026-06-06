import { defineStore } from 'pinia'
import api from '../api'

export const useJobsStore = defineStore('jobs', {
  state: () => ({ jobs: [] }),
  actions: {
    async fetchJobs() {
      const { data } = await api.get('/jobs')
      this.jobs = data
    },
  },
})
