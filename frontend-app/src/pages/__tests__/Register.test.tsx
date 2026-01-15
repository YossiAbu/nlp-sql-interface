// src/pages/__tests__/Register.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import Register from '../Register'
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

describe('Register Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const renderRegister = () => {
    return render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    )
  }

  describe('Rendering', () => {
    it('renders registration form', () => {
      renderRegister()
      
      expect(screen.getByRole('heading', { name: /register/i })).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/enter your full name/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/enter your email/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/enter your password/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument()
    })

    it('renders link to login page', () => {
      renderRegister()
      
      expect(screen.getByRole('link', { name: /login here/i })).toHaveAttribute('href', '/login')
    })
  })

  describe('Form Validation', () => {
    it('requires full name field', async () => {
      renderRegister()
      
      const nameInput = screen.getByPlaceholderText(/enter your full name/i) as HTMLInputElement
      expect(nameInput).toBeRequired()
    })

    it('requires email field', async () => {
      renderRegister()
      
      const emailInput = screen.getByPlaceholderText(/enter your email/i) as HTMLInputElement
      expect(emailInput).toBeRequired()
    })

    it('requires password field', async () => {
      renderRegister()
      
      const passwordInput = screen.getByPlaceholderText(/enter your password/i) as HTMLInputElement
      expect(passwordInput).toBeRequired()
    })
  })

  describe('Form Submission', () => {
    it('submits form with correct data', async () => {
      const user = userEvent.setup()
      
      ;(globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'User registered successfully' }),
      })
      
      renderRegister()
      
      await user.type(screen.getByPlaceholderText(/enter your full name/i), 'John Doe')
      await user.type(screen.getByPlaceholderText(/enter your email/i), 'john@example.com')
      await user.type(screen.getByPlaceholderText(/enter your password/i), 'Password123!')
      await user.click(screen.getByRole('button', { name: /register/i }))
      
      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledWith(
          `${API_BASE_URL}/register`,
          expect.objectContaining({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              full_name: 'John Doe', 
              email: 'john@example.com', 
              password: 'Password123!' 
            }),
          })
        )
      })
    })

    it('navigates to login page on successful registration', async () => {
      const user = userEvent.setup()
      
      ;(globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'User registered successfully' }),
      })
      
      renderRegister()
      
      await user.type(screen.getByPlaceholderText(/enter your full name/i), 'John Doe')
      await user.type(screen.getByPlaceholderText(/enter your email/i), 'john@example.com')
      await user.type(screen.getByPlaceholderText(/enter your password/i), 'Password123!')
      await user.click(screen.getByRole('button', { name: /register/i }))
      
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login')
      })
    })
  })

  describe('Error Handling', () => {
    it('displays error message when email already exists', async () => {
      const user = userEvent.setup()
      
      ;(globalThis.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Email already registered' }),
      })
      
      renderRegister()
      
      await user.type(screen.getByPlaceholderText(/enter your full name/i), 'John Doe')
      await user.type(screen.getByPlaceholderText(/enter your email/i), 'existing@example.com')
      await user.type(screen.getByPlaceholderText(/enter your password/i), 'Password123!')
      await user.click(screen.getByRole('button', { name: /register/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/email already registered/i)).toBeInTheDocument()
      })
    })

    it('displays generic error when fetch fails', async () => {
      const user = userEvent.setup()
      
      ;(globalThis.fetch as any).mockRejectedValueOnce(new Error('Network error'))
      
      renderRegister()
      
      await user.type(screen.getByPlaceholderText(/enter your full name/i), 'John Doe')
      await user.type(screen.getByPlaceholderText(/enter your email/i), 'john@example.com')
      await user.type(screen.getByPlaceholderText(/enter your password/i), 'Password123!')
      await user.click(screen.getByRole('button', { name: /register/i }))
      
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
      
      renderRegister()
      
      await user.type(screen.getByPlaceholderText(/enter your full name/i), 'John Doe')
      await user.type(screen.getByPlaceholderText(/enter your email/i), 'john@example.com')
      await user.type(screen.getByPlaceholderText(/enter your password/i), 'Password123!')
      await user.click(screen.getByRole('button', { name: /register/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/registering/i)).toBeInTheDocument()
      })
    })

    it('disables button during submission', async () => {
      const user = userEvent.setup()
      
      ;(globalThis.fetch as any).mockImplementationOnce(() => 
        new Promise(resolve => setTimeout(() => resolve({ ok: true, json: async () => ({}) }), 100))
      )
      
      renderRegister()
      
      await user.type(screen.getByPlaceholderText(/enter your full name/i), 'John Doe')
      await user.type(screen.getByPlaceholderText(/enter your email/i), 'john@example.com')
      await user.type(screen.getByPlaceholderText(/enter your password/i), 'Password123!')
      const button = screen.getByRole('button', { name: /register/i })
      await user.click(button)
      
      await waitFor(() => {
        expect(button).toBeDisabled()
      })
    })
  })
})

