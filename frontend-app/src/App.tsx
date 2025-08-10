import './App.css'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import QueryInterface from './pages/QueryInterface'
import History from './pages/History'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import { JSX } from 'react'

// Simple Private Route wrapper
const PrivateRoute = ({ children }: { children: JSX.Element }) => {
  const isLoggedIn = !!localStorage.getItem("user_email") // set on login
  return isLoggedIn ? children : <Navigate to="/login" replace />
}

const App = () => {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          {/* Public routes with sidebar */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected routes with sidebar */}
          <Route
            path="/interface"
            element={
              <PrivateRoute>
                <QueryInterface />
              </PrivateRoute>
            }
          />
          <Route
            path="/history"
            element={
              <PrivateRoute>
                <History />
              </PrivateRoute>
            }
          />

          {/* Redirect root to interface */}
          <Route path="/" element={<Navigate to="/interface" replace />} />

          {/* Fallback redirect for unknown paths */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
