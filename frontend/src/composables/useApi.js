import { ref, onMounted } from 'vue'

export function useApi(apiFn, options = {}) {
  const data = ref(options.default ?? null)
  const loading = ref(false)
  const error = ref(null)

  async function execute(...args) {
    loading.value = true
    error.value = null
    try {
      data.value = await apiFn(...args)
      return data.value
    } catch (e) {
      error.value = e
      if (options.onError) options.onError(e)
    } finally {
      loading.value = false
    }
  }

  if (options.immediate !== false) {
    onMounted(() => execute())
  }

  return { data, loading, error, execute, refresh: execute }
}
