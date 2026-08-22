const BASE_URL = "http://localhost:8000/routes"

async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) return null

  try {
    const res = await fetch(`${BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })

    if (!res.ok) return null

    const data = await res.json()
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    return data.access_token
  } catch {
    return null
  }
}

export async function apiFetch(path, options = {}) {
  let token = localStorage.getItem('access_token')

  const makeRequest = async (accessToken) => {
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    }
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`
    }
    return fetch(`${BASE_URL}${path}`, { ...options, headers })
  }

  let res = await makeRequest(token)

  // If unauthorized, try refreshing the token once and retry
  if (res.status === 401) {
    const newToken = await refreshAccessToken()
    if (newToken) {
      res = await makeRequest(newToken)
    } else {
      // Refresh failed too — force logout
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
      return
    }
  }

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}))
    throw new Error(errData.detail || `Request failed: ${res.status}`)
  }

  return res.json()
}