<template>
  <div class="album-card" :class="{ selected }" @click="emit('toggle', album.id)">
    <img
      v-if="album.thumbnail && !imgFailed"
      class="album-thumb"
      :src="album.thumbnail"
      :alt="album.title"
      loading="lazy"
      @error="onImgError"
    />
    <div v-else class="album-thumb-placeholder">♫</div>
    <div class="album-badge">
      <svg width="12" height="12" viewBox="0 0 10 8">
        <path d="M1 4l3 3 5-6" stroke="#0d0d0f" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <div class="album-info">
      <div class="album-title" :title="album.title">{{ album.title }}</div>
      <div class="album-artist">{{ album.artists.join(', ') }}</div>
      <div v-if="album.year" class="album-year">{{ album.year }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  album: { type: Object, required: true },
  selected: { type: Boolean, default: false },
})
const emit = defineEmits(['toggle'])

const imgFailed = ref(false)

function onImgError() {
  console.warn('[cover] failed:', props.album.title, props.album.thumbnail)
  imgFailed.value = true
}
</script>
