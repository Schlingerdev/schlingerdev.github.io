import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Trash2, Plus, RefreshCw, Clock, CheckCircle, XCircle } from 'lucide-react'
import LoginScreen from './components/LoginScreen.jsx'
import Header from './components/Header.jsx'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [authLoading, setAuthLoading] = useState(true)
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(false)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newAccount, setNewAccount] = useState({ email: '', password: '' })
  const [syncing, setSyncing] = useState(false)

  // Check authentication status on app load
  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('/api/auth/status', {
        credentials: 'include'
      })
      const data = await response.json()
      if (data.success) {
        setIsAuthenticated(data.authenticated)
      }
    } catch (error) {
      console.error('Auth status check error:', error)
      setIsAuthenticated(false)
    } finally {
      setAuthLoading(false)
    }
  }

  // Fetch accounts from API
  const fetchAccounts = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/accounts', {
        credentials: 'include'
      })
      const data = await response.json()
      if (data.success) {
        setAccounts(data.accounts)
      } else if (response.status === 401) {
        // Session expired
        setIsAuthenticated(false)
      }
    } catch (error) {
      console.error('Error fetching accounts:', error)
    } finally {
      setLoading(false)
    }
  }

  // Add new account
  const addAccount = async (e) => {
    e.preventDefault()
    if (!newAccount.email || !newAccount.password) return

    setLoading(true)
    try {
      const response = await fetch('/api/accounts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(newAccount),
      })
      const data = await response.json()
      if (data.success) {
        setNewAccount({ email: '', password: '' })
        setShowAddForm(false)
        fetchAccounts()
      } else if (response.status === 401) {
        setIsAuthenticated(false)
      }
    } catch (error) {
      console.error('Error adding account:', error)
    } finally {
      setLoading(false)
    }
  }

  // Delete account
  const deleteAccount = async (accountId) => {
    if (!confirm('Sind Sie sicher, dass Sie dieses Konto löschen möchten?')) return

    setLoading(true)
    try {
      const response = await fetch(`/api/accounts/${accountId}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      const data = await response.json()
      if (data.success) {
        fetchAccounts()
      } else if (response.status === 401) {
        setIsAuthenticated(false)
      }
    } catch (error) {
      console.error('Error deleting account:', error)
    } finally {
      setLoading(false)
    }
  }

  // Sync all accounts
  const syncAllAccounts = async () => {
    setSyncing(true)
    try {
      const response = await fetch('/api/accounts/sync', {
        method: 'POST',
        credentials: 'include'
      })
      const data = await response.json()
      if (data.success) {
        // Refresh accounts after a short delay to see updated status
        setTimeout(fetchAccounts, 2000)
      } else if (response.status === 401) {
        setIsAuthenticated(false)
      }
    } catch (error) {
      console.error('Error syncing accounts:', error)
    } finally {
      setSyncing(false)
    }
  }

  // Get status badge
  const getStatusBadge = (status) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100"><CheckCircle className="w-3 h-3 mr-1" />Aktiv</Badge>
      case 'error':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100"><XCircle className="w-3 h-3 mr-1" />Fehler</Badge>
      default:
        return <Badge className="bg-gray-100 text-gray-800 hover:bg-gray-100"><Clock className="w-3 h-3 mr-1" />Inaktiv</Badge>
    }
  }

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'Nie'
    return new Date(dateString).toLocaleString('de-DE')
  }

  // Handle login
  const handleLogin = () => {
    setIsAuthenticated(true)
    fetchAccounts()
  }

  // Handle logout
  const handleLogout = () => {
    setIsAuthenticated(false)
    setAccounts([])
  }

  // Auto-refresh accounts when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchAccounts()
      // Auto-refresh every 30 seconds
      const interval = setInterval(fetchAccounts, 30000)
      return () => clearInterval(interval)
    }
  }, [isAuthenticated])

  // Show loading screen while checking auth status
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    return <LoginScreen onLogin={handleLogin} />
  }

  // Main application UI
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header with logout */}
        <Header onLogout={handleLogout} />

        {/* Controls */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <Button 
            onClick={() => setShowAddForm(!showAddForm)}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Neues Konto hinzufügen
          </Button>
          <Button 
            onClick={syncAllAccounts}
            disabled={syncing}
            variant="outline"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Synchronisiere...' : 'Jetzt synchronisieren'}
          </Button>
        </div>

        {/* Add Account Form */}
        {showAddForm && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Neues Konto hinzufügen</CardTitle>
              <CardDescription>Geben Sie die Anmeldedaten für Ihr Manus AI Konto ein</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={addAccount} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="email">E-Mail-Adresse</Label>
                    <Input
                      id="email"
                      type="email"
                      value={newAccount.email}
                      onChange={(e) => setNewAccount({ ...newAccount, email: e.target.value })}
                      placeholder="ihre@email.com"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="password">Passwort</Label>
                    <Input
                      id="password"
                      type="password"
                      value={newAccount.password}
                      onChange={(e) => setNewAccount({ ...newAccount, password: e.target.value })}
                      placeholder="Ihr Passwort"
                      required
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button type="submit" disabled={loading}>
                    {loading ? 'Hinzufügen...' : 'Konto hinzufügen'}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setShowAddForm(false)}>
                    Abbrechen
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Accounts List */}
        <Card>
          <CardHeader>
            <CardTitle>Kontoübersicht ({accounts.length})</CardTitle>
            <CardDescription>Alle registrierten Manus AI Konten und deren Status</CardDescription>
          </CardHeader>
          <CardContent>
            {loading && accounts.length === 0 ? (
              <div className="text-center py-8">
                <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-gray-400" />
                <p className="text-gray-500">Lade Konten...</p>
              </div>
            ) : accounts.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">Keine Konten vorhanden</p>
                <Button onClick={() => setShowAddForm(true)} className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Erstes Konto hinzufügen
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-2">E-Mail-Adresse</th>
                      <th className="text-left py-3 px-2">Status</th>
                      <th className="text-left py-3 px-2">Letzter Login</th>
                      <th className="text-left py-3 px-2">Erstellt</th>
                      <th className="text-right py-3 px-2">Aktionen</th>
                    </tr>
                  </thead>
                  <tbody>
                    {accounts.map((account) => (
                      <tr key={account.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-2 font-medium">{account.email}</td>
                        <td className="py-3 px-2">{getStatusBadge(account.status)}</td>
                        <td className="py-3 px-2 text-sm text-gray-600">{formatDate(account.last_login)}</td>
                        <td className="py-3 px-2 text-sm text-gray-600">{formatDate(account.created_at)}</td>
                        <td className="py-3 px-2 text-right">
                          <Button
                            onClick={() => deleteAccount(account.id)}
                            variant="outline"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-500">
          <p>Automatische Synchronisierung erfolgt täglich um 0:00 Uhr</p>
        </div>
      </div>
    </div>
  )
}

export default App
