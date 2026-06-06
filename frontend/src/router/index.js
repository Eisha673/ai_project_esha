import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import JobsView from '../views/JobsView.vue'
import PipelineView from '../views/PipelineView.vue'
import CandidatesView from '../views/CandidatesView.vue'
import OffersView from '../views/OffersView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: DashboardView },
    { path: '/jobs', component: JobsView },
    { path: '/pipeline/:jobId?', component: PipelineView },
    { path: '/candidates', component: CandidatesView },
    { path: '/offers', component: OffersView },
  ],
})
