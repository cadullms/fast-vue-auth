<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const message = ref('')

onMounted(async () => {
  try {
    console.log('Fetching message now from API...')
    const response = await axios.get('/api/hello',
      {
        withCredentials: true,
        headers: {
          'Access-Control-Allow-Origin': 'http://127.0.0.1:5173'
        }
      })
    console.log(`Got return code ${response.status} from API...`)
    console.log(`Got text ${response.data} from API...`)
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
