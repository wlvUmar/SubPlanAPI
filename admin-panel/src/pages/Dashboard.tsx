import { useEffect, useState } from 'react'
import { getStats } from '../services/api'
import { Users, Package, CreditCard, DollarSign } from 'lucide-react'

export default function Dashboard() {
  const [stats, setStats] = useState({
    users: 0,
    active_subscriptions: 0,
    total_payments: 0,
    paid_payments: 0,
    total_revenue: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const data = await getStats()
      setStats(data)
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    { label: 'Total Users', value: stats.users, icon: Users, color: 'bg-blue-500' },
    { label: 'Active Subscriptions', value: stats.active_subscriptions, icon: Package, color: 'bg-green-500' },
    { label: 'Total Payments', value: stats.total_payments, icon: CreditCard, color: 'bg-purple-500' },
    { label: 'Total Revenue', value: `$${stats.total_revenue.toFixed(2)}`, icon: DollarSign, color: 'bg-yellow-500' },
  ]

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon
          return (
            <div key={index} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-800 mt-2">{stat.value}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

