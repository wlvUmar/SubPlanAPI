import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { login as apiLogin, getCurrentUser } from '../services/api'

interface User {
  user_id: string
  name: string
  email: string
  role: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  const fetchUser = async (authToken: string | null) => {
    if (!authToken) {
      setLoading(false)
      return
    }
    try {
      const userData = await getCurrentUser(authToken)
      if (userData.role === 'admin') {
        setUser(userData)
      } else {
        logout()
      }
    } catch (error) {
      logout()
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUser(token)
  }, [])

  const login = async (email: string, password: string) => {
    const response = await apiLogin(email, password)
    const accessToken = response.access
    setToken(accessToken)
    localStorage.setItem('token', accessToken)
    const userData = await getCurrentUser(accessToken)
    if (userData.role === 'admin') {
      setUser(userData)
    } else {
      throw new Error('Access denied: Admin role required')
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

