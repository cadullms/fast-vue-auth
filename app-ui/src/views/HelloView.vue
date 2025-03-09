<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const message = ref('')

onMounted(async () => {
  try {
    const response = await axios.get('/api/hello')
    message.value = response.data.message
  } catch (error) {
    console.error('Error fetching message:', error)
  }
})
</script>

<template>
  <div>
    <h1>Hello View</h1>
    <p>{{ message }}</p>
  </div>
</template>

<style scoped>
/* Add any styles if necessary */
</style>
