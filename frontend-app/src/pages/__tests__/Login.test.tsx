// src/pages/__tests__/Login.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import Login from '../Login'
import { API_BASE_URL } from '@/lib/api'


// Mock useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// Mock fetch
globalThis.fetch = vi.fn() as any

describe('Login Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  const renderLogin = () => {
    return render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )
  }

  describe('Rendering', () => {
    it('renders login form', () => {
      renderLogin()
      
      expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/enter your email/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/enter your password/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument()
    })

    it('renders link to registration page', () => {
      renderLogin()
      
      expect(screen.getByRole('link', { name: /register here/i })).toHaveAttribute('href', '/register')
    })
  })

  describe('Form Validation', () => {
    it('requires email field', async () => {
      renderLogin()
      
      const emailInput = screen.getByPlaceholderText(/enter your email/i) as HTMLInputElement
      expect(emailInput).toBeRequired()
    })

    it('requires password field', async () => {
      renderLogin()
      
      const passwordInput = screen.getByPlaceholderText(/enter your password/i) as HTMLInputElement
      expect(passwordInput).toBeRequired()
    })
  })

  describe('Form Submission', () => {
    it('submits form with correct credentials', async () => {
      const user = userEvent.setup()
      
      ;(globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Login successful', full_name: 'Test User' }),
      })
      
      renderLogin()
      
      await user.type(screen.getByPlaceholderText(/enter your email/i), 'test@example.com')
      await user.type(screen.getByPlaceholderText(/enter your password/i), 'password123')
      await user.click(screen.getByRole('button', { name: /login/i }))
      
      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledWith(
          `${API_BASE_URL}/login`,
          expect.objectContaining({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ email: 'test@example.com', password: 'password123' }),
          })
        )
      })
    })

    it('navigates to interface page on successful login', async () => {
      const user = userEvent.setup()
      
      ;(globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Login successful', full_name: 'Test User' }),
      })
      
      renderLogin()
      
      await user.type(screen.getByPlaceholderText(/enter your email/i), 'test@example.com')
      await user.type(screen.getByPlaceholderText(/enter your password/i), 'password123')
      await user.click(screen.getByRole('button', { name: /login/i }))
      
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/interface')
      })
    })

    it('saves email to localStorage on successful login', async () => {
      const user = userEvent.setup()
      
      ;(globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Login successful' }),
      })
      
      renderLogin()
      
      await user.type(screen.getByPlaceholderText(/enter your email/i), 'test@example.com')
      await user.type(screen.getByPlaceholderText(/enter your password/i), 'password123')
      await user.click(screen.getByRole('button', { name: /login/i }))
      
      await waitFor(() => {
        expect(localStorage.getItem('user_email')).toBe('test@example.com')
      })
    })

    it('dispatches auth:changed event on successful login', async () => {
      const user = userEvent.setup()
      const dispatchSpy = vi.spyOn(window, 'dispatchEvent')
      
      ;(globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Login successful' }),
      })
      
      renderLogin()
      
      await user.type(screen.getByPlaceholderText(/enter your email/i), 'test@example.com')
      await user.type(screen.getByPlaceholderText(/enter your password/i), 'password123')
      await user.click(screen.getByRole('button', { name: /login/i }))
      
      await waitFor(() => {
        expect(dispatchSpy).toHaveBeenCalled()
      })
    })
  })

  describe('Error Handling', () => {
    it('displays error message on failed login', async () => {
      const user = userEvent.setup()
      
      ;(globalThis.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Invalid credentials' }),
      })
      
      renderLogin()
      
      await user.type(screen.getByPlaceholderText(/enter your email/i), 'wrong@example.com')
      await user.type(screen.getByPlaceholderText(/enter your password/i), 'wrongpass')
      await user.click(screen.getByRole('button', { name: /login/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument()
      })
    })

    it('displays generic error when fetch fails', async () => {
      const user = userEvent.setup()
      
      ;(globalThis.fetch as any).mockRejectedValueOnce(new Error('Network error'))
      
      renderLogin()
      
      await user.type(screen.getByPlaceholderText(/enter your email/i), 'test@example.com')
      await user.type(screen.getByPlaceholderText(/enter your password/i), 'password123')
      await user.click(screen.getByRole('button', { name: /login/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument()
      })
    })
  })

  describe('Loading State', () => {
    it('shows loading text during submission', async () => {
      const user = userEvent.setup()
      
      ;(globalThis.fetch as any).mockImplementationOnce(() => 
        new Promise(resolve => setTimeout(() => resolve({ ok: true, json: async () => ({}) }), 100))
      )
      
      renderLogin()
      
      await user.type(screen.getByPlaceholderText(/enter your email/i), 'test@example.com')
      await user.type(screen.getByPlaceholderText(/enter your password/i), 'password123')
      await user.click(screen.getByRole('button', { name: /login/i }))
      
      expect(screen.getByText(/logging in/i)).toBeInTheDocument()
    })

    it('disables button during submission', async () => {
      const user = userEvent.setup()
      
      ;(globalThis.fetch as any).mockImplementationOnce(() => 
        new Promise(resolve => setTimeout(() => resolve({ ok: true, json: async () => ({}) }), 100))
      )
      
      renderLogin()
      
      await user.type(screen.getByPlaceholderText(/enter your email/i), 'test@example.com')
      await user.type(screen.getByPlaceholderText(/enter your password/i), 'password123')
      const button = screen.getByRole('button', { name: /login/i })
      await user.click(button)
      
      await waitFor(() => {
        expect(button).toBeDisabled()
      })
    })
  })
})

