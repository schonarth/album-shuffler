export async function fetchStatus() {
  try {
    const res = await fetch('/api/status')
    return await res.json()
  } catch {
    return { ok: false, auth: false, message: 'Server unreachable' }
  }
}

export async function fetchArtists() {
  const res = await fetch('/api/artists')
  const data = await res.json()
  if (data.error) throw new Error(data.error)
  return data
}

export async function fetchAlbums(artistIds = [], mode = 'library') {
  const params = new URLSearchParams()
  if (artistIds.length) params.set('artists', artistIds.join(','))
  if (artistIds.length && mode === 'all') params.set('mode', 'all')
  const url = '/api/albums' + (params.toString() ? '?' + params : '')
  const res = await fetch(url)
  const data = await res.json()
  if (data.error) throw new Error(data.error)
  return data
}

export async function createPlaylist(name, albumIds, overwrite) {
  const res = await fetch('/api/playlist', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, album_ids: albumIds, overwrite }),
  })
  const data = await res.json()
  if (data.error) throw new Error(data.error)
  return data
}
