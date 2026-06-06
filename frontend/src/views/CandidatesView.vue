<script setup>
import { onMounted } from 'vue'
import CandidateKanban from '../components/CandidateKanban.vue'
import { useCandidatesStore } from '../stores/candidates'

const store = useCandidatesStore()
onMounted(() => store.fetchCandidates())
</script>

<template>
  <section>
    <h1 class="page-title">Candidates</h1>
    <p class="muted">Kanban stages include Nemotron scores, bias flags, and full reasoning side panels.</p>
    <CandidateKanban style="margin-top:24px" :candidates="store.candidates" />
  </section>
</template>
