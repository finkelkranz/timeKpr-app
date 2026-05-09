import { useState, useEffect } from 'react'
import axios from 'axios'
import { ThemeProvider } from './context/ThemeContext'
import { ToastProvider } from './components/ToastProvider'
import Skeleton from './components/Skeleton'
import Login from './components/Login'
import Dashboard from './components/Dashboard.tsx'
import Settings from './components/Settings'
import './App.css'

// Configure axios to use backend URL
const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:8000' : window.location.origin
axios.defaults.baseURL = API_BASE_URL

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

interface AppContentProps {
  isAuthenticated: boolean
  users: User[]
  loading: boolean
  loadingUsers: boolean
  error: string | null
  showSettings: boolean
  onLogin: (password: string) => Promise<void>
  onLogout: () => void
  onUpdateTime: (username: string, seconds: number) => Promise<void>
  onSettingsClick: () => void
  onCloseSettings: () => void
}

function AppContent({
  isAuthenticated,
  users,
  loading,
  loadingUsers,
  error,
  showSettings,
  onLogin,
  onLogout,
  onUpdateTime,
  onSettingsClick,
  onCloseSettings
}: AppContentProps) {
  // Show toast for successful actions
  const handleUpdateTime = async (username: string, seconds: number) => {
    await onUpdateTime(username, seconds);
  };

  const DashboardWithLoading = () => (
    <>
      <Dashboard
        users={users}
        onLogout={onLogout}
        onUpdateTime={handleUpdateTime}
        error={error}
        onSettingsClick={onSettingsClick}
      />
      {showSettings && <Settings onClose={onCloseSettings} />}
    </>
  );

  return isAuthenticated ? (
    loadingUsers ? (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <header className="bg-gradient-to-r from-blue-600 to-blue-800 dark:from-gray-800 dark:to-gray-900 shadow-lg sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <h1 className="text-xl md:text-2xl font-bold text-white">timekpr Admin</h1>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <Skeleton.UserGrid count={4} />
        </main>
      </div>
    ) : (
      <DashboardWithLoading />
    )
  ) : (
    <Login onLogin={onLogin} loading={loading} error={error} />
  );
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingUsers, setLoadingUsers] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showSettings, setShowSettings] = useState(false)

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
      setLoadingUsers(true)
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
    } finally {
      setLoadingUsers(false)
    }
  }

  const updateTimeLeft = async (username: string, seconds: number) => {
    try {
      await axios.post(`/api/stats/users/${username}/add-time`, {
        seconds: seconds,
        period: "day"
      })
      await fetchUsers() // Refresh data
    } catch (err) {
      setError('Failed to update time')
    }
  }

  const toggleSettings = () => {
    setShowSettings(!showSettings)
  }

  return (
    <ThemeProvider>
      <ToastProvider>
        <AppContent
          isAuthenticated={isAuthenticated}
          users={users}
          loading={loading}
          loadingUsers={loadingUsers}
          error={error}
          showSettings={showSettings}
          onLogin={handleLogin}
          onLogout={handleLogout}
          onUpdateTime={updateTimeLeft}
          onSettingsClick={toggleSettings}
          onCloseSettings={() => setShowSettings(false)}
        />
      </ToastProvider>
    </ThemeProvider>
  )
}

export default App
