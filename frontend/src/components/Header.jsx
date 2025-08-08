import { Button } from '@/components/ui/button.jsx'
import { LogOut } from 'lucide-react'

function Header({ onLogout }) {
  const handleLogout = async () => {
    try {
      const response = await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      })

      const data = await response.json()
      if (data.success) {
        onLogout()
      }
    } catch (error) {
      console.error('Logout error:', error)
      // Logout auch bei Fehler durchführen
      onLogout()
    }
  }

  return (
    <div className="text-center mb-8">
      <div className="flex justify-between items-center mb-4">
        <div></div>
        <h1 className="text-4xl font-bold text-gray-900">Manus AI Account Manager</h1>
        <Button
          onClick={handleLogout}
          variant="outline"
          size="sm"
          className="text-red-600 hover:text-red-700 hover:bg-red-50"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Abmelden
        </Button>
      </div>
      <p className="text-gray-600">Verwalten Sie mehrere Manus AI Accounts mit automatischer täglicher Aktualisierung</p>
    </div>
  )
}

export default Header

