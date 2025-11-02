import { useEffect, useState } from 'react'
import { getSubscriptions, updateSubscriptionStatus } from '../services/api'

interface Subscription {
  subscription_id: string
  status: string
  start_date: string
  end_date?: string
  user_id: string
  name: string
}

export default function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    loadSubscriptions()
  }, [statusFilter])

  const loadSubscriptions = async () => {
    try {
      setLoading(true)
      const data = await getSubscriptions(0, 100, statusFilter || undefined)
      setSubscriptions(data)
    } catch (error) {
      console.error('Failed to load subscriptions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (subscriptionId: string, newStatus: string) => {
    try {
      await updateSubscriptionStatus(subscriptionId, newStatus)
      loadSubscriptions()
    } catch (error) {
      console.error('Failed to update subscription status:', error)
    }
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Subscriptions</h1>
      </div>

      <div className="bg-white rounded-lg shadow mb-6 p-4">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="canceled">Canceled</option>
          <option value="expired">Expired</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Plan
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Start Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  End Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {subscriptions.map((sub) => (
                <tr key={sub.subscription_id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500">
                    {sub.subscription_id.substring(0, 8)}...
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 capitalize">
                    {sub.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <select
                      value={sub.status}
                      onChange={(e) => handleStatusChange(sub.subscription_id, e.target.value)}
                      className="text-sm border border-gray-300 rounded px-2 py-1"
                    >
                      <option value="active">Active</option>
                      <option value="canceled">Canceled</option>
                      <option value="expired">Expired</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(sub.start_date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {sub.end_date ? new Date(sub.end_date).toLocaleDateString() : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    User: {sub.user_id.substring(0, 8)}...
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

