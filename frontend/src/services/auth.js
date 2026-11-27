import api from './api.js'

export async function getSession() { const { data } = await api.get('/auth/session/'); return data.user }
export async function login(username, password) { await api.get('/auth/session/'); const { data } = await api.post('/auth/login/', { username, password }); return data.user }
export async function logout() { await api.post('/auth/logout/') }
