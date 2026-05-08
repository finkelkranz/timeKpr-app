import { useState } from 'react'
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
}

function Dashboard({ users, onLogout, onUpdateTime, error }: DashboardProps) {
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [newTime, setNewTime] = useState('')

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const getChartData = (user: User) => ({
    labels: ['Today', 'Week', 'Month'],
    datasets: [
      {
        label: 'Time Left',
        data: [user.time_left_today, user.time_left_week, user.time_left_month],
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
      {
        label: 'Total Limit',
        data: [user.daily_limit, user.weekly_limit, user.monthly_limit],
        backgroundColor: 'rgba(16, 185, 129, 0.5)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 1,
      },
    ],
  })

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Screen Time Overview',
      },
    },
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">timekpr Admin</h1>
            </div>
            <button
              onClick={onLogout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* User Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {users.map((user) => (
            <div
              key={user.username}
              className="bg-white overflow-hidden shadow rounded-lg cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => setSelectedUser(user)}
            >
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                      <span className="text-white font-medium text-sm">
                        {user.username.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {user.username}
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {formatTime(user.time_left_today)} left today
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-5 py-3">
                <div className="text-sm">
                  <div className="text-gray-500">
                    Week: {formatTime(user.time_left_week)}
                  </div>
                  <div className="text-gray-500">
                    Month: {formatTime(user.time_left_month)}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Selected User Details */}
        {selectedUser && (
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                {selectedUser.username} - Details
              </h2>
              <button
                onClick={() => setSelectedUser(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Chart */}
              <div>
                <Bar data={getChartData(selectedUser)} options={chartOptions} />
              </div>

              {/* Controls */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Adjust Today's Time (seconds)
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="number"
                      value={newTime}
                      onChange={(e) => setNewTime(e.target.value)}
                      placeholder="3600"
                      className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary"
                    />
                    <button
                      onClick={async () => {
                        const seconds = parseInt(newTime)
                        if (!isNaN(seconds)) {
                          await onUpdateTime(selectedUser.username, seconds)
                          setNewTime('')
                        }
                      }}
                      className="bg-primary hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                    >
                      Update
                    </button>
                  </div>
                </div>

                <div className="text-sm text-gray-600">
                  <p><strong>Daily Limit:</strong> {formatTime(selectedUser.daily_limit)}</p>
                  <p><strong>Weekly Limit:</strong> {formatTime(selectedUser.weekly_limit)}</p>
                  <p><strong>Monthly Limit:</strong> {formatTime(selectedUser.monthly_limit)}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default Dashboard