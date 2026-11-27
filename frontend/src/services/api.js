import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL?.trim() || '/api/v1'

const api = axios.create({
  baseURL,
  headers: {
    Accept: 'application/json',
  },
  timeout: 10000,
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
})

export default api
