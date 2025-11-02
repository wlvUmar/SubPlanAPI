import { useEffect, useState } from 'react'
import { getInvoices } from '../services/api'

interface Invoice {
  invoice_id: string
  user_id: string
  subscription_id: string
  amount: number
  pdf_url: string
  created_at: string
}

export default function Invoices() {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadInvoices()
  }, [])

  const loadInvoices = async () => {
    try {
      setLoading(true)
      const data = await getInvoices(0, 100)
      setInvoices(data)
    } catch (error) {
      console.error('Failed to load invoices:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Invoices</h1>
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
                  User ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Subscription ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  PDF
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {invoices.map((invoice) => (
                <tr key={invoice.invoice_id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500">
                    {invoice.invoice_id.substring(0, 8)}...
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    ${invoice.amount.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                    {invoice.user_id.substring(0, 8)}...
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                    {invoice.subscription_id.substring(0, 8)}...
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {invoice.pdf_url ? (
                      <a
                        href={invoice.pdf_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View PDF
                      </a>
                    ) : (
                      <span className="text-gray-400">No PDF</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(invoice.created_at).toLocaleString()}
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

