<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'
import OfferModal from '../components/OfferModal.vue'

const offers = ref([])
const selected = ref(null)

onMounted(async () => {
  offers.value = (await api.get('/offers')).data
})
</script>

<template>
  <section>
    <h1 class="page-title">Offers</h1>
    <div class="grid" style="margin-top:24px">
      <article v-for="offer in offers" :key="offer.id" class="card" @click="selected = offer">
        <strong>{{ offer.status }}</strong>
        <p class="muted">{{ offer.candidate_id }}</p>
      </article>
    </div>
    <OfferModal :offer="selected" @close="selected = null" />
  </section>
</template>
