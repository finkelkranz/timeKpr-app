import { useState } from 'react'
import { useTheme } from '../context/ThemeContext'
import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

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

interface DashboardProps {
  users: User[]
  onLogout: () => void
  onUpdateTime: (username: string, seconds: number) => Promise<void>
  error: string | null
  onSettingsClick: () => void
}

function Dashboard({ users, onLogout, onUpdateTime, error, onSettingsClick }: DashboardProps) {
  const { toggleTheme } = useTheme();
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [hoursInput, setHoursInput] = useState("0")
  const [minutesInput, setMinutesInput] = useState("15")
  const [showTimeModal, setShowTimeModal] = useState(false)

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    if (hours > 0 && minutes > 0) {
      return `${hours}h ${minutes}m`
    } else if (hours > 0) {
      return `${hours}h`
    } else if (minutes > 0) {
      return `${minutes}m`
    }
    return "0m"
  }

  const calculatePercentage = (remaining: number, limit: number) => {
    if (limit === 0) return 100
    return Math.min(100, Math.max(0, (remaining / limit) * 100))
  }

  const getProgressBarColor = (percentage: number) => {
    if (percentage > 50) return 'bg-green-500 dark:bg-green-400'
    if (percentage > 20) return 'bg-amber-500 dark:bg-amber-400'
    return 'bg-red-500 dark:bg-red-400'
  }

  const getDayChartData = (user: User) => ({
    labels: ["Used", "Remaining"],
    datasets: [
      {
        label: "Time",
        data: [user.daily_limit - user.time_left_today, user.time_left_today],
        backgroundColor: ["rgba(239, 68, 68, 0.8)", "rgba(59, 130, 246, 0.8)"],
        borderColor: ["rgba(239, 68, 68, 1)", "rgba(59, 130, 246, 1)"],
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  })

  const getWeekChartData = (user: User) => ({
    labels: ["Used", "Remaining"],
    datasets: [
      {
        label: "Time",
        data: [user.weekly_limit - user.time_left_week, user.time_left_week],
        backgroundColor: ["rgba(239, 68, 68, 0.8)", "rgba(59, 130, 246, 0.8)"],
        borderColor: ["rgba(239, 68, 68, 1)", "rgba(59, 130, 246, 1)"],
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  })

  const getMonthChartData = (user: User) => ({
    labels: ["Used", "Remaining"],
    datasets: [
      {
        label: "Time",
        data: [user.monthly_limit - user.time_left_month, user.time_left_month],
        backgroundColor: ["rgba(239, 68, 68, 0.8)", "rgba(59, 130, 246, 0.8)"],
        borderColor: ["rgba(239, 68, 68, 1)", "rgba(59, 130, 246, 1)"],
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  })

  const baseChartOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 1500,
      easing: 'easeInOutQuart',
      from: {
        y: 0,
      },
    },
    plugins: {
      legend: { display: false },
      title: { 
        display: true, 
        font: { size: 14 },
        color: '#374151',
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: { size: 14, weight: 'bold' as const },
        bodyFont: { size: 13 },
        borderColor: 'rgba(59, 130, 246, 0.5)',
        borderWidth: 1,
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || ''
            const value = context.raw as number
            return `${label}: ${formatTime(value)}`
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
        ticks: { 
          callback: (value: string | number) => {
            const num = typeof value === 'string' ? parseInt(value) : value
            return formatTime(num)
          },
          color: '#6b7280',
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: '#6b7280',
        },
      },
    },
  }



  const handleAddTime = async (seconds: number) => {
    if (!selectedUser) return
    try {
      await onUpdateTime(selectedUser.username, seconds)
      setShowTimeModal(false)
      setHoursInput("0")
      setMinutesInput("15")
    } catch (err) {}
  }

  const handlePresetTime = async (seconds: number) => {
    if (!selectedUser) return
    await handleAddTime(seconds)
  }

  const getTotalSeconds = () => {
    const hours = parseInt(hoursInput) || 0
    const minutes = parseInt(minutesInput) || 0
    return hours * 3600 + minutes * 60
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <header className="bg-gradient-to-r from-blue-600 to-blue-800 dark:from-gray-800 dark:to-gray-900 shadow-lg sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-xl md:text-2xl font-bold text-gray-900 dark:text-gray-100">timekpr Admin</h1>
            <div className="flex items-center gap-2">
              <button
                onClick={toggleTheme}
                className="p-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                aria-label="Toggle theme"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              </button>
              <button
                onClick={onSettingsClick}
                className="p-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                aria-label="Settings"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
              <button onClick={onLogout} className="bg-red-600 hover:bg-red-700 active:bg-red-800 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200">Logout</button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-4 sm:py-6 lg:py-8 px-4 sm:px-6 lg:px-8">
        {error && <div className="mb-4 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-400 dark:border-red-600 text-red-700 dark:text-red-300 px-4 py-3 rounded-md"><p className="font-medium">{error}</p></div>}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-8">
          {users.map((user) => {
            const dayPercent = calculatePercentage(user.time_left_today, user.daily_limit)
            const weekPercent = calculatePercentage(user.time_left_week, user.weekly_limit)
            const monthPercent = calculatePercentage(user.time_left_month, user.monthly_limit)
            return (
              <div key={user.username} className="bg-white dark:bg-gray-800 overflow-hidden shadow-md rounded-xl cursor-pointer hover:shadow-lg hover:-translate-y-1 transition-all duration-300 active:scale-[0.98] active:translate-y-0" onClick={() => setSelectedUser(user)}>
                <div className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-white font-bold text-lg">{user.username.charAt(0).toUpperCase()}</span>
                    </div>
                    <div className="min-w-0 flex-1">
                      <dt className="text-sm font-medium text-gray-600 dark:text-gray-400 truncate">{user.username}</dt>
                      <dd className="text-lg font-bold text-gray-900 dark:text-gray-100 truncate">{formatTime(user.time_left_today)}</dd>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700/50 px-4 py-3 space-y-2">
                  <div>
                    <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1"><span>Today</span><span>{dayPercent}%</span></div>
                    <div className="h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                      <div className={`h-full ${getProgressBarColor(dayPercent)} transition-all duration-300`} style={{width: `${dayPercent}%`}} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1"><span>Week</span><span>{weekPercent}%</span></div>
                    <div className="h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                      <div className={`h-full ${getProgressBarColor(weekPercent)} transition-all duration-300`} style={{width: `${weekPercent}%`}} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1"><span>Month</span><span>{monthPercent}%</span></div>
                    <div className="h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                      <div className={`h-full ${getProgressBarColor(monthPercent)} transition-all duration-300`} style={{width: `${monthPercent}%`}} />
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {selectedUser && (
          <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700 sticky top-0 bg-white dark:bg-gray-800 z-10">
                <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">{selectedUser.username}</h2>
                <button onClick={() => { setSelectedUser(null); setShowTimeModal(false); }} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 p-2 rounded-full transition-colors" aria-label="Close">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
              </div>
              <div className="p-4 sm:p-6">
                <div className="grid grid-cols-3 gap-3 mb-6">
                  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 text-center">
                    <div className="text-2xl font-bold text-blue-700 dark:text-blue-300">{formatTime(selectedUser.time_left_today)}</div>
                    <div className="text-xs text-blue-600 dark:text-blue-400 mt-1">Left Today</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">of {formatTime(selectedUser.daily_limit)}</div>
                  </div>
                  <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4 text-center">
                    <div className="text-2xl font-bold text-green-700 dark:text-green-300">{formatTime(selectedUser.time_left_week)}</div>
                    <div className="text-xs text-green-600 dark:text-green-400 mt-1">Left This Week</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">of {formatTime(selectedUser.weekly_limit)}</div>
                  </div>
                  <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 text-center">
                    <div className="text-2xl font-bold text-purple-700 dark:text-purple-300">{formatTime(selectedUser.time_left_month)}</div>
                    <div className="text-xs text-purple-600 dark:text-purple-400 mt-1">Left This Month</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">of {formatTime(selectedUser.monthly_limit)}</div>
                  </div>
                </div>
                <div className="space-y-6 mb-6">
                  <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                    <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Daily Usage</h3>
                    <div className="h-48">
                      <Bar 
                        data={getDayChartData(selectedUser)} 
                        options={{...baseChartOptions, plugins: {...baseChartOptions.plugins, title: {display: true, text: "Today"}}}}
                      />
                    </div>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                    <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Weekly Usage</h3>
                    <div className="h-48">
                      <Bar 
                        data={getWeekChartData(selectedUser)} 
                        options={{...baseChartOptions, plugins: {...baseChartOptions.plugins, title: {display: true, text: "This Week"}}}}
                      />
                    </div>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                    <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Monthly Usage</h3>
                    <div className="h-48">
                      <Bar 
                        data={getMonthChartData(selectedUser)} 
                        options={{...baseChartOptions, plugins: {...baseChartOptions.plugins, title: {display: true, text: "This Month"}}}}
                      />
                    </div>
                  </div>
                </div>
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4">
                  <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Add More Time</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
                    <button onClick={() => handlePresetTime(15 * 60)} className="bg-white dark:bg-gray-700 border-2 border-blue-500 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-600 active:bg-blue-100 dark:active:bg-gray-500 font-medium py-3 px-2 rounded-lg transition-all duration-200 text-sm">+15 min</button>
                    <button onClick={() => handlePresetTime(30 * 60)} className="bg-white dark:bg-gray-700 border-2 border-blue-500 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-600 active:bg-blue-100 dark:active:bg-gray-500 font-medium py-3 px-2 rounded-lg transition-all duration-200 text-sm">+30 min</button>
                    <button onClick={() => handlePresetTime(60 * 60)} className="bg-white dark:bg-gray-700 border-2 border-blue-500 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-600 active:bg-blue-100 dark:active:bg-gray-500 font-medium py-3 px-2 rounded-lg transition-all duration-200 text-sm">+1 hour</button>
                    <button onClick={() => handlePresetTime(2 * 60 * 60)} className="bg-white dark:bg-gray-700 border-2 border-blue-500 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-600 active:bg-blue-100 dark:active:bg-gray-500 font-medium py-3 px-2 rounded-lg transition-all duration-200 text-sm">+2 hours</button>
                  </div>
                  <button onClick={() => setShowTimeModal(true)} className="w-full bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-medium py-3 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    Custom Amount
                  </button>
                </div>
                {showTimeModal && (
                  <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-sm">
                      <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">Add Custom Time</h3>
                      <div className="space-y-3">
                        <div className="flex gap-2">
                          <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Hours</label>
                            <input type="number" value={hoursInput} onChange={(e) => setHoursInput(e.target.value)} min="0" max="24" className="w-full rounded-lg border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-3 text-gray-900 dark:text-gray-100" placeholder="0" />
                          </div>
                          <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Minutes</label>
                            <input type="number" value={minutesInput} onChange={(e) => setMinutesInput(e.target.value)} min="0" max="59" className="w-full rounded-lg border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-3 text-gray-900 dark:text-gray-100" placeholder="0" />
                          </div>
                        </div>
                        <div className="text-center text-sm text-gray-500 dark:text-gray-400">Total: {formatTime(getTotalSeconds())}</div>
                        <div className="flex gap-2 mt-4">
                          <button onClick={() => setShowTimeModal(false)} className="flex-1 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-medium py-3 rounded-lg transition-colors">Cancel</button>
                          <button onClick={async () => { const seconds = getTotalSeconds(); if (seconds > 0) { await handleAddTime(seconds); } }} disabled={getTotalSeconds() === 0} className="flex-1 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 disabled:bg-blue-300 text-white font-medium py-3 rounded-lg transition-colors disabled:cursor-not-allowed">Add Time</button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        {selectedUser && (
          <button onClick={() => setShowTimeModal(true)} className="lg:hidden fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white p-4 rounded-full shadow-lg transition-all duration-200 z-40" aria-label="Add Time">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </button>
        )}
        {selectedUser && (
          <button onClick={() => setShowTimeModal(true)} className="hidden lg:flex fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white p-4 rounded-full shadow-lg transition-all duration-200 z-40 items-center justify-center gap-2" aria-label="Add Time">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <span className="text-sm font-medium">Add Time</span>
          </button>
        )}
      </main>
    </div>
  )
}

export default Dashboard
