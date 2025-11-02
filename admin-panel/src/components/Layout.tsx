import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { 
  LayoutDashboard, 
  Users, 
  CreditCard, 
  FileText, 
  Package,
  Receipt,
  LogOut
} from 'lucide-react'

export default function Layout() {
  const { logout } = useAuth()
  const location = useLocation()

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/users', label: 'Users', icon: Users },
    { path: '/subscriptions', label: 'Subscriptions', icon: Package },
    { path: '/payments', label: 'Payments', icon: CreditCard },
    { path: '/invoices', label: 'Invoices', icon: Receipt },
    { path: '/plans', label: 'Plans', icon: FileText },
  ]

  return (
    <div className="flex h-screen bg-gray-100">
      <aside className="w-64 bg-white shadow-lg">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-gray-800">Admin Panel</h1>
        </div>
        <nav className="mt-6">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-6 py-3 text-gray-700 hover:bg-gray-100 ${
                  isActive ? 'bg-blue-50 text-blue-600 border-r-4 border-blue-600' : ''
                }`}
              >
                <Icon className="w-5 h-5 mr-3" />
                {item.label}
              </Link>
            )
          })}
        </nav>
        <div className="absolute bottom-0 w-64 p-6">
          <button
            onClick={logout}
            className="flex items-center w-full px-4 py-2 text-gray-700 hover:bg-gray-100 rounded"
          >
            <LogOut className="w-5 h-5 mr-3" />
            Logout
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}

