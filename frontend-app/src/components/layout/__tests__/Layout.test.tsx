// src/components/layout/__tests__/Layout.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import Layout from '../Layout'

// Mock navigation
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// Mock UserAPI
vi.mock('@/entities/User', () => ({
  UserAPI: {
    me: vi.fn(),
  },
  User: {} as any,
}))

// Mock fetch for logout
globalThis.fetch = vi.fn() as any

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}))

describe('Layout Component', () => {
  let mockUserMe: any

  const mockUser = {
    id: 'user1',
    email: 'test@example.com',
    full_name: 'Test User',
  }

  beforeEach(async () => {
    vi.clearAllMocks()
    localStorage.clear()
    // Get the mocked function
    const userModule = await import('@/entities/User')
    mockUserMe = userModule.UserAPI.me as any
  })

  const renderLayout = (children = <div>Test Content</div>) => {
    return render(
      <BrowserRouter>
        <Layout>{children}</Layout>
      </BrowserRouter>
    )
  }

  describe('Loading State', () => {
    it('shows loading skeleton while fetching user', async () => {
      mockUserMe.mockImplementationOnce(() => 
        new Promise(resolve => setTimeout(() => resolve(mockUser), 100))
      )

      const { container } = renderLayout()
      
      // Check for loading skeleton in footer
      const skeleton = container.querySelector('.animate-pulse')
      expect(skeleton).toBeInTheDocument()
    })

    it('hides loading skeleton after user is fetched', async () => {
      mockUserMe.mockResolvedValueOnce(mockUser)

      const { container } = renderLayout()
      
      await waitFor(() => {
        const skeleton = container.querySelector('.animate-pulse')
        expect(skeleton).not.toBeInTheDocument()
      })
    })
  })

  describe('Unauthenticated State', () => {
    it('shows login button when user is not authenticated', async () => {
      mockUserMe.mockRejectedValueOnce(new Error('Not authenticated'))

      renderLayout()

      await waitFor(() => {
        expect(screen.getByText(/login.*sign up/i)).toBeInTheDocument()
      })
    })

    it('navigates to login page when login button is clicked', async () => {
      const user = userEvent.setup()
      mockUserMe.mockRejectedValueOnce(new Error('Not authenticated'))

      renderLayout()

      await waitFor(() => {
        expect(screen.getByText(/login.*sign up/i)).toBeInTheDocument()
      })

      const loginButton = screen.getByText(/login.*sign up/i).closest('button')
      if (loginButton) await user.click(loginButton)

      expect(mockNavigate).toHaveBeenCalledWith('/login')
    })
  })

  describe('Authenticated State', () => {
    it('displays user information when authenticated', async () => {
      mockUserMe.mockResolvedValueOnce(mockUser)

      renderLayout()

      await waitFor(() => {
        expect(screen.getByText('Test User')).toBeInTheDocument()
        expect(screen.getByText('test@example.com')).toBeInTheDocument()
      })
    })

    it('displays user initial in avatar when user has full name', async () => {
      mockUserMe.mockResolvedValueOnce(mockUser)

      const { container } = renderLayout()

      await waitFor(() => {
        // Check for the user's initial "T" in the avatar
        expect(container.textContent).toContain('T')
      })
    })

    it('shows logout button when user is authenticated', async () => {
      mockUserMe.mockResolvedValueOnce(mockUser)

      renderLayout()

      await waitFor(() => {
        // Find the logout icon button
        const logoutButton = screen.getByRole('button', { name: '' })
        expect(logoutButton).toBeInTheDocument()
      })
    })
  })

  describe('Logout Functionality', () => {
    it('calls logout API and clears localStorage when logout is clicked', async () => {
      const user = userEvent.setup()
      mockUserMe.mockResolvedValueOnce(mockUser)
      ;(globalThis.fetch as any).mockResolvedValueOnce({ ok: true })

      localStorage.setItem('user_email', 'test@example.com')

      const { container } = renderLayout()

      await waitFor(() => {
        expect(screen.getByText('Test User')).toBeInTheDocument()
      })

      // Find logout button (it's an icon button in the footer)
      const buttons = container.querySelectorAll('button')
      const logoutButton = Array.from(buttons).find(btn => 
        btn.querySelector('svg')?.classList.contains('lucide-log-out')
      )

      if (logoutButton) await user.click(logoutButton)

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledWith(
          'http://localhost:8000/logout',
          expect.objectContaining({
            method: 'POST',
            credentials: 'include',
          })
        )
        expect(localStorage.getItem('user_email')).toBeNull()
        expect(mockNavigate).toHaveBeenCalledWith('/login')
      })
    })

    it('dispatches auth:changed event on logout', async () => {
      const user = userEvent.setup()
      const dispatchSpy = vi.spyOn(window, 'dispatchEvent')
      mockUserMe.mockResolvedValueOnce(mockUser)
      ;(globalThis.fetch as any).mockResolvedValueOnce({ ok: true })

      const { container } = renderLayout()

      await waitFor(() => {
        expect(screen.getByText('Test User')).toBeInTheDocument()
      })

      const buttons = container.querySelectorAll('button')
      const logoutButton = Array.from(buttons).find(btn => 
        btn.querySelector('svg')?.classList.contains('lucide-log-out')
      )

      if (logoutButton) await user.click(logoutButton)

      await waitFor(() => {
        expect(dispatchSpy).toHaveBeenCalled()
      })
    })

    it('handles logout even if API call fails', async () => {
      const user = userEvent.setup()
      mockUserMe.mockResolvedValueOnce(mockUser)
      ;(globalThis.fetch as any).mockRejectedValueOnce(new Error('Network error'))

      localStorage.setItem('user_email', 'test@example.com')

      const { container } = renderLayout()

      await waitFor(() => {
        expect(screen.getByText('Test User')).toBeInTheDocument()
      })

      const buttons = container.querySelectorAll('button')
      const logoutButton = Array.from(buttons).find(btn => 
        btn.querySelector('svg')?.classList.contains('lucide-log-out')
      )

      if (logoutButton) await user.click(logoutButton)

      await waitFor(() => {
        expect(localStorage.getItem('user_email')).toBeNull()
        expect(mockNavigate).toHaveBeenCalledWith('/login')
      })
    })
  })

  describe('Navigation', () => {
    it('renders navigation links', async () => {
      mockUserMe.mockResolvedValueOnce(mockUser)

      renderLayout()

      await waitFor(() => {
        expect(screen.getByText('Query Interface')).toBeInTheDocument()
        expect(screen.getByText('My History')).toBeInTheDocument()
      })
    })

    it('renders QueryMind branding', async () => {
      mockUserMe.mockResolvedValueOnce(mockUser)

      const { container } = renderLayout()

      await waitFor(() => {
        // QueryMind appears in multiple places, just check it's in the container
        expect(container.textContent).toContain('QueryMind')
        expect(container.textContent).toContain('Natural Language SQL')
      })
    })
  })

  describe('Event Listener Handling', () => {
    it('refetches user when auth:changed event is dispatched', async () => {
      mockUserMe.mockResolvedValueOnce(null)
      mockUserMe.mockResolvedValueOnce(mockUser)

      renderLayout()

      await waitFor(() => {
        expect(screen.getByText(/login.*sign up/i)).toBeInTheDocument()
      })

      // Clear the first call
      mockUserMe.mockClear()

      // Dispatch auth:changed event
      window.dispatchEvent(new Event('auth:changed'))

      await waitFor(() => {
        expect(mockUserMe).toHaveBeenCalled()
      })
    })
  })

  describe('Children Rendering', () => {
    it('renders children content', async () => {
      mockUserMe.mockResolvedValueOnce(mockUser)

      renderLayout(<div data-testid="test-child">Child Content</div>)

      await waitFor(() => {
        expect(screen.getByTestId('test-child')).toBeInTheDocument()
        expect(screen.getByText('Child Content')).toBeInTheDocument()
      })
    })
  })

  describe('Theme Toggle', () => {
    it('renders theme toggle component', async () => {
      mockUserMe.mockResolvedValueOnce(mockUser)

      renderLayout()

      await waitFor(() => {
        // ThemeToggle shows either "Light Mode" or "Dark Mode"
        const themeButton = screen.queryByText(/light mode|dark mode/i)
        expect(themeButton).toBeInTheDocument()
      })
    })
  })
})

