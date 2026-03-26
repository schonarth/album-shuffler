<template>
  <div class="panel" style="margin-bottom: 20px;">
    <div class="panel-header">
      <span class="panel-title">Artists</span>
      <span class="panel-count">{{ filteredArtists.length }} / {{ artists.length }}</span>
    </div>

    <div class="search-wrap">
      <input
        v-model="query"
        type="text"
        placeholder="Search artists…"
        autocomplete="off"
      />
      <button v-if="query" class="search-clear visible" @click="query = ''">✕</button>
    </div>

    <div id="artists-list">
      <div
        v-for="artist in filteredArtists"
        :key="artist.id"
        class="artist-item"
        :class="{ selected: modelValue.has(artist.id) }"
        @click="toggle(artist.id)"
      >
        <div class="artist-check">
          <svg v-if="modelValue.has(artist.id)" width="10" height="8" viewBox="0 0 10 8">
            <path d="M1 4l3 3 5-6" stroke="#0d0d0f" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="artist-name" :title="artist.name">{{ artist.name }}</div>
      </div>
      <div v-if="!artists.length" class="empty-state">
        <div class="empty-icon">🎤</div>
        <div>No artists found</div>
      </div>
    </div>

    <div class="select-bar">
      <button class="btn-text" @click="selectAll">All</button>
      <button class="btn-text muted" @click="deselectAll">None</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  artists: { type: Array, default: () => [] },
  modelValue: { type: Set, default: () => new Set() },
})
const emit = defineEmits(['update:modelValue'])

const query = ref('')

const filteredArtists = computed(() => {
  const q = query.value.toLowerCase()
  return q ? props.artists.filter(a => a.name.toLowerCase().includes(q)) : props.artists
})

function toggle(id) {
  const next = new Set(props.modelValue)
  next.has(id) ? next.delete(id) : next.add(id)
  emit('update:modelValue', next)
}

function selectAll() {
  const next = new Set(props.modelValue)
  filteredArtists.value.forEach(a => next.add(a.id))
  emit('update:modelValue', next)
}

function deselectAll() {
  emit('update:modelValue', new Set())
}
</script>
