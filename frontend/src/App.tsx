import { useState, useEffect } from 'react'
import axios from 'axios'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import './App.css'

interface User {
  username: string
  time_left_today: number
  time_left_week: number
  time_left_month: number
  daily_limit: number
  weekly_limit: number
  monthly_limit: number
  allowed_hours: number[]
  allowed_weekdays: number[]
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Check if we have a valid token on mount
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      setIsAuthenticated(true)
      fetchUsers()
    }
  }, [])

  const handleLogin = async (password: string) => {
    try {
      setLoading(true)
      setError(null)
      const response = await axios.post('/api/auth/login', { password })
      const { access_token } = response.data

      localStorage.setItem('token', access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      setIsAuthenticated(true)
      await fetchUsers()
    } catch (err) {
      setError('Invalid password')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
    setIsAuthenticated(false)
    setUsers([])
  }

  const fetchUsers = async () => {
    try {
      const response = await axios.get('/api/stats/users')
      const usernames = response.data

      // Fetch stats for each user
      const userPromises = usernames.map(async (username: string) => {
        const statsResponse = await axios.get(`/api/stats/users/${username}`)
        return statsResponse.data
      })

      const userStats = await Promise.all(userPromises)
      setUsers(userStats)
    } catch (err) {
      setError('Failed to fetch user data')
    }
  }

  const updateTimeLeft = async (username: string, seconds: number) => {
    try {
      await axios.put(`/api/config/users/${username}/time-left-today`, null, {
        params: { seconds }
      })
      await fetchUsers() // Refresh data
    } catch (err) {
      setError('Failed to update time')
    }
  }

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} loading={loading} error={error} />
  }

  return (
    <Dashboard
      users={users}
      onLogout={handleLogout}
      onUpdateTime={updateTimeLeft}
      error={error}
    />
  )
}

export default App