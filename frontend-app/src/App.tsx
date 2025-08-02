import './App.css'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Home from './pages/Home'
import QueryInterface from './pages/QueryInterface'
import History from './pages/History'
import Layout from './components/layout/Layout'

const App = () => {
  return (
    <BrowserRouter>
      <Layout currentPageName="interface">
        <Routes>
          {/* 👇 Redirect default path to /interface */}
          <Route path="/" element={<Navigate to="/interface" replace />} />
          <Route path="/interface" element={<QueryInterface />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
