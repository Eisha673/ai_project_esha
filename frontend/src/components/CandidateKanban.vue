<script setup>
import { computed, ref } from 'vue'
import NimScoreBadge from './NimScoreBadge.vue'

const props = defineProps({
  candidates: { type: Array, default: () => [] },
})

const selected = ref(null)
const stages = ['applied', 'shortlisted', 'assessed', 'interviewed', 'offered']
const labels = {
  applied: 'Applied',
  shortlisted: 'Shortlisted',
  assessed: 'Assessed',
  interviewed: 'Interviewed',
  offered: 'Offered',
}

const grouped = computed(() => Object.fromEntries(stages.map(stage => [stage, props.candidates.filter(c => c.stage === stage)])))
</script>

<template>
  <div style="display:grid;grid-template-columns:repeat(5,minmax(180px,1fr));gap:16px;overflow:auto">
    <section v-for="stage in stages" :key="stage" class="card" style="padding:12px;background:#f8fafc">
      <h3 style="margin:0 0 12px;font-size:14px">{{ labels[stage] }}</h3>
      <article v-for="candidate in grouped[stage]" :key="candidate.id" class="card" style="padding:12px;margin-bottom:10px" @click="selected = candidate">
        <strong>{{ candidate.full_name }}</strong>
        <p class="muted" style="margin:4px 0 10px;font-size:12px">{{ candidate.email }}</p>
        <NimScoreBadge :score="candidate.nim_screen_score" :bias-flag="candidate.nim_bias_flagged" />
      </article>
    </section>
  </div>
  <aside v-if="selected" class="card" style="position:fixed;top:0;right:0;width:min(420px,100vw);height:100vh;z-index:9;overflow:auto;border-radius:0" @click.self="selected = null">
    <button class="button secondary" style="float:right" @click="selected = null">Close</button>
    <h2>{{ selected.full_name }}</h2>
    <NimScoreBadge :score="selected.nim_screen_score" :bias-flag="selected.nim_bias_flagged" />
    <h3>Nemotron Reasoning</h3>
    <p class="mono" style="white-space:pre-wrap">{{ selected.nim_screen_reasoning || 'No reasoning captured yet.' }}</p>
  </aside>
</template>
