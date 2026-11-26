import api from './api.js'

export async function searchCities(query) {
  const { data } = await api.get('/weather/cities/', {
    params: { q: query },
  })
  return data.results
}

export async function getCurrentWeather(location) {
  const { data } = await api.get('/weather/current/', {
    params: {
      latitude: location.latitude,
      longitude: location.longitude,
    },
  })
  return data
}

export async function getForecast(location, days = 5) {
  const { data } = await api.get('/weather/forecast/', {
    params: {
      latitude: location.latitude,
      longitude: location.longitude,
      days,
    },
  })
  return data
}

export async function getActiveAlerts(city) {
  const { data } = await api.get('/alerts/', {
    params: { city, page_size: 5 },
  })
  return data.results
}
