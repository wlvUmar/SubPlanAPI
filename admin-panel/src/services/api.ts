import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const login = async (email: string, password: string) => {
  const response = await api.post('/user/login', { email, password })
  return response.data
}

export const getCurrentUser = async (token: string) => {
  const response = await api.get('/user/me')
  return response.data
}

export const getStats = async () => {
  const response = await api.get('/admin/stats')
  return response.data
}

export const getUsers = async (skip = 0, limit = 100, search?: string, role?: string) => {
  const params: any = { skip, limit }
  if (search) params.search = search
  if (role) params.role = role
  const response = await api.get('/admin/users', { params })
  return response.data
}

export const getUser = async (userId: string) => {
  const response = await api.get(`/admin/users/${userId}`)
  return response.data
}

export const updateUserStatus = async (userId: string, isActive: boolean) => {
  const response = await api.patch(`/admin/users/${userId}/activate`, null, {
    params: { is_active: isActive },
  })
  return response.data
}

export const verifyUser = async (userId: string) => {
  const response = await api.patch(`/admin/users/${userId}/verify`)
  return response.data
}

export const updateUserRole = async (userId: string, role: string) => {
  const response = await api.patch(`/admin/users/${userId}/role`, null, {
    params: { role },
  })
  return response.data
}

export const getSubscriptions = async (skip = 0, limit = 100, status?: string) => {
  const params: any = { skip, limit }
  if (status) params.status = status
  const response = await api.get('/admin/subscriptions', { params })
  return response.data
}

export const updateSubscriptionStatus = async (subscriptionId: string, status: string) => {
  const response = await api.patch(`/admin/subscriptions/${subscriptionId}/status`, null, {
    params: { status },
  })
  return response.data
}

export const getPayments = async (skip = 0, limit = 100, status?: string) => {
  const params: any = { skip, limit }
  if (status) params.status = status
  const response = await api.get('/admin/payments', { params })
  return response.data
}

export const updatePaymentStatus = async (paymentId: string, status: string, providerTxnId?: string) => {
  const params: any = { status }
  if (providerTxnId) params.provider_txn_id = providerTxnId
  const response = await api.patch(`/admin/payments/${paymentId}/status`, null, { params })
  return response.data
}

export const getInvoices = async (skip = 0, limit = 100) => {
  const response = await api.get('/admin/invoices', { params: { skip, limit } })
  return response.data
}

export const getPlans = async () => {
  const response = await api.get('/plans')
  return response.data
}

export const createPlan = async (plan: any) => {
  const response = await api.post('/plans', plan)
  return response.data
}

export const updatePlan = async (planName: string, plan: any) => {
  const response = await api.put(`/plans/${planName}`, plan)
  return response.data
}

export const deletePlan = async (planName: string) => {
  await api.delete(`/plans/${planName}`)
}

export default api

