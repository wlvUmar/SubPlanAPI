import { useEffect, useState } from 'react'
import { getPlans, createPlan, updatePlan, deletePlan } from '../services/api'

interface Plan {
  name: string
  price: number
  interval: number
  description?: string
}

export default function Plans() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingPlan, setEditingPlan] = useState<Plan | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    price: 0,
    interval: 30,
    description: '',
  })

  useEffect(() => {
    loadPlans()
  }, [])

  const loadPlans = async () => {
    try {
      setLoading(true)
      const data = await getPlans()
      setPlans(data)
    } catch (error) {
      console.error('Failed to load plans:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingPlan) {
        await updatePlan(editingPlan.name, formData)
      } else {
        await createPlan(formData)
      }
      setShowModal(false)
      setEditingPlan(null)
      setFormData({ name: '', price: 0, interval: 30, description: '' })
      loadPlans()
    } catch (error) {
      console.error('Failed to save plan:', error)
    }
  }

  const handleEdit = (plan: Plan) => {
    setEditingPlan(plan)
    setFormData({
      name: plan.name,
      price: plan.price,
      interval: plan.interval,
      description: plan.description || '',
    })
    setShowModal(true)
  }

  const handleDelete = async (planName: string) => {
    if (confirm(`Are you sure you want to delete plan "${planName}"?`)) {
      try {
        await deletePlan(planName)
        loadPlans()
      } catch (error) {
        console.error('Failed to delete plan:', error)
      }
    }
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Plans</h1>
        <button
          onClick={() => {
            setEditingPlan(null)
            setFormData({ name: '', price: 0, interval: 30, description: '' })
            setShowModal(true)
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Create Plan
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <div key={plan.name} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-gray-800 capitalize">{plan.name}</h3>
                <span className="text-2xl font-bold text-blue-600">${plan.price}</span>
              </div>
              <p className="text-gray-600 mb-4">{plan.description || 'No description'}</p>
              <p className="text-sm text-gray-500 mb-4">Interval: {plan.interval} days</p>
              <div className="flex gap-2">
                <button
                  onClick={() => handleEdit(plan)}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(plan.name)}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full">
            <h2 className="text-2xl font-bold mb-6">
              {editingPlan ? 'Edit Plan' : 'Create Plan'}
            </h2>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Plan Name
                </label>
                <select
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  disabled={!!editingPlan}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="">Select plan</option>
                  <option value="basic">Basic</option>
                  <option value="business">Business</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Price
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Interval (days)
                </label>
                <input
                  type="number"
                  value={formData.interval}
                  onChange={(e) => setFormData({ ...formData, interval: parseInt(e.target.value) })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  rows={3}
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  {editingPlan ? 'Update' : 'Create'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false)
                    setEditingPlan(null)
                  }}
                  className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

