<template>
  <div class="panel config-panel">
    <div class="panel-header">
      <span class="panel-title">Playlist</span>
    </div>
    <div class="panel-body">
      <div>
        <label class="field-label" for="playlist-name">Playlist name</label>
        <input
          id="playlist-name"
          v-model="playlistName"
          type="text"
          class="text-input"
          placeholder="My Album Shuffle"
        />
      </div>

      <div class="toggle-row">
        <div>
          <span class="toggle-label">Overwrite existing</span>
          <span class="toggle-sub">Replace playlist with same name</span>
        </div>
        <label class="toggle">
          <input v-model="overwrite" type="checkbox" />
          <div class="toggle-track"></div>
          <div class="toggle-thumb"></div>
        </label>
      </div>

      <div class="toggle-row" :style="{ opacity: overwrite ? 1 : 0.4 }">
        <div>
          <span class="toggle-label">Confirm before overwrite</span>
          <span class="toggle-sub">Show a prompt before replacing</span>
        </div>
        <label class="toggle">
          <input v-model="confirmOverwrite" type="checkbox" :disabled="!overwrite" />
          <div class="toggle-track"></div>
          <div class="toggle-thumb"></div>
        </label>
      </div>

      <button
        class="btn-generate"
        :disabled="generating || !canGenerate"
        @click="generate"
      >
        <div v-if="generating" class="spinner"></div>
        <span>{{ generating ? 'Creating…' : 'Shuffle &amp; Create' }}</span>
      </button>
    </div>
  </div>

  <div class="panel summary-panel">
    <div class="panel-body">
      <div class="summary-row">
        <span>Artists selected</span>
        <span class="summary-val">{{ selectedArtistCount }}</span>
      </div>
      <div class="summary-row">
        <span>Albums selected</span>
        <span class="summary-val">{{ selectedAlbumCount }}</span>
      </div>
      <div class="summary-row">
        <span>Playlist name</span>
        <span class="summary-val">{{ playlistName || '—' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  selectedAlbumCount: { type: Number, default: 0 },
  selectedArtistCount: { type: Number, default: 0 },
  selectedAlbumIds: { type: Array, default: () => [] },
  generating: { type: Boolean, default: false },
})
const emit = defineEmits(['generate'])

const playlistName = ref('')
const overwrite = ref(true)
const confirmOverwrite = ref(false)

const canGenerate = computed(() => playlistName.value.trim() && props.selectedAlbumCount > 0)

function generate() {
  if (!canGenerate.value) return
  if (overwrite.value && confirmOverwrite.value) {
    if (!confirm(`Replace existing playlist "${playlistName.value.trim()}"?`)) return
  }
  emit('generate', {
    name: playlistName.value.trim(),
    albumIds: props.selectedAlbumIds,
    overwrite: overwrite.value,
  })
}
</script>
