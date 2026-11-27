import api, { setCsrfToken } from './api.js'

async function fetchSession() {
  const { data } = await api.get('/auth/session/')
  setCsrfToken(data.csrf_token)
  return data
}

export async function getSession() {
  const data = await fetchSession()
  return data.user
}

export async function login(username, password) {
  await fetchSession()
  const { data } = await api.post('/auth/login/', { username, password })
  setCsrfToken(data.csrf_token)
  return data.user
}

export async function logout() {
  await fetchSession()
  await api.post('/auth/logout/')
  setCsrfToken(null)
}
