import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Signup from './pages/Signup'
import Login from './pages/Login'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import ProtectedRoute from './components/ProtectedRoute'
import Trade from './pages/trade'
import Transactions from './pages/Transactions'
import Markets from './pages/Markets'
import Analytics from './pages/Analytics'

function Navbar() {
  const { isLoggedIn, logout } = useAuth()

  return (
    <nav className="w-full bg-slate-900 border-b border-slate-800 px-6 py-4 flex items-center justify-between text-slate-200">
      <div className="flex items-center gap-6">
        <span className="font-bold text-xl text-blue-500">CryptoPulse</span>
        <Link to="/" className="hover:text-white transition">Home</Link>
        {isLoggedIn && (
          <>
            <Link to="/dashboard" className="hover:text-white transition">Dashboard</Link>
            <Link to="/trade/BTCUSDT" className="hover:text-white transition">Trade</Link>
            <Link to="/transactions" className="hover:text-white transition">Transactions</Link>
            <Link to="/markets" className="hover:text-white transition">Markets</Link>
            <Link to="/analytics">Analytics</Link>
            <Link to={`/analytics/${symbol}`} className="text-purple-400 underline">Chart</Link>
          </>
        )}
      </div>

      <div>
        {isLoggedIn ? (
          <button onClick={logout} className="text-red-500 hover:text-red-400 font-medium transition">
            Logout
          </button>
        ) : (
          <div className="flex gap-4">
            <Link to="/login" className="hover:text-white transition">Login</Link>
            <Link to="/signup" className="hover:text-white transition">Signup</Link>
          </div>
        )}
      </div>
    </nav>
  )
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          {/* Default trade route */}
          <Route path="/trade" element={
            <ProtectedRoute>
              <Trade />
            </ProtectedRoute>
          } />
          {/* Dynamic symbol trade route */}
          <Route path="/trade/:symbol" element={
            <ProtectedRoute>
              <Trade />
            </ProtectedRoute>
          } />
          <Route
            path="/transactions"
            element={
          <ProtectedRoute>
            <Transactions />
           </ProtectedRoute>
          }/>
          <Route path="/markets" element={<Markets />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/analytics/:symbol" element={<Analytics />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App