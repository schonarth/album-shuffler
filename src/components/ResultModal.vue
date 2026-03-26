<template>
  <Teleport to="body">
    <div v-if="visible" id="result-overlay" class="visible" @click.self="emit('close')">
      <div class="result-card">
        <div class="result-header">
          <div class="result-icon">🎵</div>
          <div class="result-title">{{ result?.action === 'overwritten' ? 'Updated!' : 'Created!' }}</div>
          <div class="result-sub">{{ result?.name }}</div>
        </div>
        <div class="result-body">
          <div class="result-stat">
            <span class="result-stat-label">Action</span>
            <span class="result-stat-val">{{ result?.action }}</span>
          </div>
          <div class="result-stat">
            <span class="result-stat-label">Total tracks</span>
            <span class="result-stat-val">{{ result?.total_tracks }}</span>
          </div>
          <div class="result-stat">
            <span class="result-stat-label">Albums</span>
            <span class="result-stat-val">{{ result?.album_order?.length }}</span>
          </div>
          <div v-if="result?.album_order?.length" class="result-order">
            <div
              v-for="(album, i) in result.album_order"
              :key="i"
              class="result-order-item"
            >
              <span class="result-order-num">{{ i + 1 }}</span>
              <span class="result-order-title">{{ album.title }}</span>
              <span class="result-order-tracks">{{ album.tracks }} tracks</span>
            </div>
          </div>
        </div>
        <div class="result-actions">
          <a :href="result?.url" target="_blank" class="btn-open">Open in YT Music</a>
          <button class="btn-close" @click="emit('close')">Close</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  result: { type: Object, default: null },
  visible: { type: Boolean, default: false },
})
const emit = defineEmits(['close'])
</script>
