import { ref } from 'vue'

const message = ref('')
const visible = ref(false)
let _timer = null

export function useToast() {
  function showToast(msg, duration = 4000) {
    console.error('[toast]', msg)
    message.value = msg
    visible.value = true
    clearTimeout(_timer)
    _timer = setTimeout(() => { visible.value = false }, duration)
  }

  return { message, visible, showToast }
}
