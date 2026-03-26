<template>
  <div class="app">
    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.visible.value" id="toast">{{ toast.message.value }}</div>
    </Transition>

    <!-- Loading screen -->
    <div id="loading-screen" :class="{ hidden: !loading }">
      <div class="loading-logo">ALBUM <span>SHUFFLER</span></div>
      <div class="loading-bar-wrap"><div class="loading-bar"></div></div>
      <div class="loading-msg">Loading library…</div>
    </div>

    <header>
      <div class="logo">ALBUM <span>SHUFFLER</span></div>
      <div>
        <div class="subtitle">YouTube Music</div>
      </div>
    </header>

    <div v-if="authError" id="auth-banner" class="visible">
      ⚠ {{ authError }} — run <code>bash setup.sh</code> to authenticate.
    </div>

    <div class="columns">
      <div>
        <ArtistList
          :artists="allArtists"
          :model-value="selectedArtists"
          @update:model-value="onArtistsChange"
        />
        <AlbumGrid
          :albums="allAlbums"
          :model-value="selectedAlbums"
          :has-artist-filter="selectedArtists.size > 0"
          :mode="albumMode"
          @update:model-value="val => selectedAlbums = val"
          @update:mode="onModeChange"
        />
      </div>
      <div class="sidebar">
        <PlaylistPanel
          :selected-album-count="selectedAlbums.size"
          :selected-artist-count="selectedArtists.size"
          :selected-album-ids="[...selectedAlbums]"
          :generating="generating"
          @generate="onGenerate"
        />
      </div>
    </div>

    <ResultModal
      :result="result"
      :visible="showResult"
      @close="showResult = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchStatus, fetchArtists, fetchAlbums, createPlaylist } from './api.js'
import { useToast } from './composables/useToast.js'
import ArtistList from './components/ArtistList.vue'
import AlbumGrid from './components/AlbumGrid.vue'
import PlaylistPanel from './components/PlaylistPanel.vue'
import ResultModal from './components/ResultModal.vue'

const toast = useToast()

const loading = ref(true)
const authError = ref('')
const allArtists = ref([])
const allAlbums = ref([])
const selectedArtists = ref(new Set())
const selectedAlbums = ref(new Set())
const albumMode = ref('library')
const generating = ref(false)
const result = ref(null)
const showResult = ref(false)

async function onArtistsChange(newSet) {
  selectedArtists.value = newSet
  selectedAlbums.value = new Set()
  albumMode.value = newSet.size ? 'all' : 'library'
  try {
    allAlbums.value = await fetchAlbums([...newSet], albumMode.value)
  } catch (e) {
    toast.showToast('Failed to load albums: ' + e.message)
  }
}

async function onModeChange(mode) {
  albumMode.value = mode
  selectedAlbums.value = new Set()
  try {
    allAlbums.value = await fetchAlbums([...selectedArtists.value], mode)
  } catch (e) {
    toast.showToast('Failed to load albums: ' + e.message)
  }
}

async function onGenerate({ name, albumIds, overwrite }) {
  generating.value = true
  try {
    result.value = await createPlaylist(name, albumIds, overwrite)
    showResult.value = true
  } catch (e) {
    toast.showToast('Error: ' + e.message, 6000)
  } finally {
    generating.value = false
  }
}

onMounted(async () => {
  const status = await fetchStatus()
  if (!status.auth) {
    authError.value = status.message || 'Not authenticated'
  }

  try {
    allArtists.value = await fetchArtists()
    allAlbums.value = await fetchAlbums()
  } catch (e) {
    toast.showToast('Failed to load library: ' + e.message, 8000)
  } finally {
    loading.value = false
  }
})
</script>
