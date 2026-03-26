<template>
  <div class="panel" id="albums-wrap">
    <div class="panel-header">
      <span class="panel-title">Albums</span>
      <div v-if="hasArtistFilter" class="albums-mode-row">
        <span class="mode-side" :class="{ active: mode === 'library' }">Library only</span>
        <label class="toggle">
          <input type="checkbox" :checked="mode === 'all'" @change="emit('update:mode', $event.target.checked ? 'all' : 'library')" />
          <div class="toggle-track"></div>
          <div class="toggle-thumb"></div>
        </label>
        <span class="mode-side" :class="{ active: mode === 'all' }">All albums</span>
      </div>
    </div>

    <div class="albums-search-wrap">
      <input
        v-model="query"
        type="text"
        placeholder="Search albums…"
        autocomplete="off"
      />
      <button v-if="query" class="albums-search-clear visible" @click="query = ''">✕</button>
    </div>

    <div class="albums-select-bar">
      <button class="btn-text" @click="selectAll">All</button>
      <button class="btn-text muted" @click="deselectAll">None</button>
      <span class="panel-count">{{ filteredAlbums.length }} / {{ albums.length }}</span>
    </div>

    <div id="albums-grid">
      <template v-if="filteredAlbums.length">
        <AlbumCard
          v-for="album in filteredAlbums"
          :key="album.id"
          :album="album"
          :selected="modelValue.has(album.id)"
          @toggle="toggleAlbum"
        />
      </template>
      <div v-else class="empty-state" style="grid-column: 1 / -1;">
        <div class="empty-icon">{{ albums.length ? '🔍' : '💿' }}</div>
        <div>{{ albums.length ? 'No albums match your search' : 'No albums found' }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AlbumCard from './AlbumCard.vue'

const props = defineProps({
  albums: { type: Array, default: () => [] },
  modelValue: { type: Set, default: () => new Set() },
  hasArtistFilter: { type: Boolean, default: false },
  mode: { type: String, default: 'library' },
})
const emit = defineEmits(['update:modelValue', 'update:mode'])

const query = ref('')

const filteredAlbums = computed(() => {
  const q = query.value.toLowerCase()
  return q
    ? props.albums.filter(a =>
        a.title.toLowerCase().includes(q) ||
        a.artists.join(' ').toLowerCase().includes(q)
      )
    : props.albums
})

function toggleAlbum(id) {
  const next = new Set(props.modelValue)
  next.has(id) ? next.delete(id) : next.add(id)
  emit('update:modelValue', next)
}

function selectAll() {
  const next = new Set(props.modelValue)
  filteredAlbums.value.forEach(a => next.add(a.id))
  emit('update:modelValue', next)
}

function deselectAll() {
  emit('update:modelValue', new Set())
}
</script>
