import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL?.trim() || '/api/v1'
let csrfToken = null

const api = axios.create({
  baseURL,
  headers: {
    Accept: 'application/json',
  },
  timeout: 10000,
  withCredentials: true,
  withXSRFToken: false,
})

api.interceptors.request.use((config) => {
  if (
    csrfToken &&
    ['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase())
  ) {
    config.headers['X-CSRFToken'] = csrfToken
  }
  return config
})

export function setCsrfToken(token) {
  csrfToken = token || null
}

export default api
