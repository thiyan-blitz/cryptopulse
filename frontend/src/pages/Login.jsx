import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    try {
      const res = await fetch('http://localhost:8000/routes/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username, password }),
      })

      if (!res.ok) {
        throw new Error('Invalid username or password')
      }

      const data = await res.json()
      login(data.access_token, data.refresh_token)
      navigate('/')
      
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="p-8 max-w-sm mx-auto">
      <h1 className="text-2xl font-bold mb-4">Login</h1>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <input
          type="text"
          placeholder="Username or email"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="border p-2 rounded"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border p-2 rounded"
        />

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <button type="submit" className="bg-blue-600 text-white p-2 rounded cursor-pointer">
          Log In
        </button>
      </form>
    </div>
  )
}

export default Login