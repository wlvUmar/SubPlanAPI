import { useEffect, useState } from 'react'
import { getPayments, updatePaymentStatus } from '../services/api'

interface Payment {
  payment_id: string
  user_id: string
  subscription_id: string
  amount: number
  currency: string
  status: string
  provider_txn_id?: string
  created_at: string
}

export default function Payments() {
  const [payments, setPayments] = useState<Payment[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    loadPayments()
  }, [statusFilter])

  const loadPayments = async () => {
    try {
      setLoading(true)
      const data = await getPayments(0, 100, statusFilter || undefined)
      setPayments(data)
    } catch (error) {
      console.error('Failed to load payments:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (paymentId: string, newStatus: string) => {
    try {
      await updatePaymentStatus(paymentId, newStatus)
      loadPayments()
    } catch (error) {
      console.error('Failed to update payment status:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Payments</h1>
      </div>

      <div className="bg-white rounded-lg shadow mb-6 p-4">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Statuses</option>
          <option value="paid">Paid</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
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
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Transaction ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {payments.map((payment) => (
                <tr key={payment.payment_id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500">
                    {payment.payment_id.substring(0, 8)}...
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {payment.amount.toFixed(2)} {payment.currency.toUpperCase()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(payment.status)}`}>
                      {payment.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {payment.provider_txn_id || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(payment.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <select
                      value={payment.status}
                      onChange={(e) => handleStatusChange(payment.payment_id, e.target.value)}
                      className="text-sm border border-gray-300 rounded px-2 py-1"
                    >
                      <option value="paid">Paid</option>
                      <option value="pending">Pending</option>
                      <option value="failed">Failed</option>
                    </select>
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

