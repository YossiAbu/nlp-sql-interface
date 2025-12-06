// src/pages/__tests__/History.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import History from '../History'
import { Query } from '@/entities/Query'

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
    login: vi.fn(),
  },
}))

// Mock API functions
vi.mock('@/lib/api', () => ({
  fetchHistory: vi.fn(),
  clearHistory: vi.fn(),
}))

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}))

// Mock window.confirm
globalThis.confirm = vi.fn()

describe('History Page', () => {
  let mockUserMe: any
  let mockUserLogin: any
  let mockFetchHistory: any
  let mockClearHistory: any

  const mockUser = {
    id: 'user1',
    email: 'test@example.com',
    full_name: 'Test User',
  }

  const mockQueries: Query[] = [
    {
      id: '1',
      user_id: 'user1',
      question: 'Show all players',
      sql_query: 'SELECT * FROM players',
      status: 'success',
      execution_time: 150,
      results: 'Query results',
      raw_rows: [{ name: 'Messi', ovr: 93 }],
      created_date: '2024-01-15T10:30:00Z',
      error_message: null,
    },
    {
      id: '2',
      user_id: 'user1',
      question: 'Invalid query',
      sql_query: '',
      status: 'error',
      execution_time: 50,
      results: '',
      raw_rows: [],
      created_date: '2024-01-14T10:30:00Z',
      error_message: 'Query failed',
    },
  ]

  beforeEach(async () => {
    vi.clearAllMocks()
    // Get the mocked functions
    const userModule = await import('@/entities/User')
    const apiModule = await import('@/lib/api')
    mockUserMe = userModule.UserAPI.me as any
    mockUserLogin = userModule.UserAPI.login as any
    mockFetchHistory = apiModule.fetchHistory as any
    mockClearHistory = apiModule.clearHistory as any
  })

  const renderHistory = () => {
    return render(
      <BrowserRouter>
        <History />
      </BrowserRouter>
    )
  }

  describe('Loading State', () => {
    it('shows loading spinner while fetching data', () => {
      mockUserMe.mockImplementationOnce(() => 
        new Promise(resolve => setTimeout(() => resolve(mockUser), 100))
      )

      const { container } = renderHistory()
      
      // Look for the spinner with animate-spin class
      const spinner = container.querySelector('.animate-spin')
      expect(spinner).toBeInTheDocument()
    })
  })

  describe('Unauthenticated State', () => {
    it('shows login prompt when user is not authenticated', async () => {
      mockUserMe.mockRejectedValueOnce(new Error('Not authenticated'))

      renderHistory()

      await waitFor(() => {
        expect(screen.getByText(/view your query history/i)).toBeInTheDocument()
        expect(screen.getByText(/log in to access your personal query history/i)).toBeInTheDocument()
      })
    })

    it('calls UserAPI.login when login button is clicked', async () => {
      const user = userEvent.setup()
      mockUserMe.mockRejectedValueOnce(new Error('Not authenticated'))
      mockUserLogin.mockResolvedValueOnce({})

      // Mock location.reload
      delete (window as any).location
      window.location = { reload: vi.fn() } as any

      renderHistory()

      await waitFor(() => {
        expect(screen.getByText(/login to continue/i)).toBeInTheDocument()
      })

      const loginButton = screen.getByText(/login to continue/i).closest('button')
      if (loginButton) await user.click(loginButton)

      expect(mockUserLogin).toHaveBeenCalled()
    })
  })

  describe('Authenticated State with Queries', () => {
    beforeEach(() => {
      mockUserMe.mockResolvedValue(mockUser)
      mockFetchHistory.mockResolvedValue({ items: mockQueries })
    })

    it('renders page heading', async () => {
      renderHistory()

      await waitFor(() => {
        expect(screen.getByText(/my query history/i)).toBeInTheDocument()
      })
    })

    it('displays query count badges', async () => {
      renderHistory()

      await waitFor(() => {
        expect(screen.getByText(/2 total queries/i)).toBeInTheDocument()
        expect(screen.getByText(/1 successful/i)).toBeInTheDocument()
        expect(screen.getByText(/1 errors/i)).toBeInTheDocument()
      })
    })

    it('displays all queries', async () => {
      renderHistory()

      await waitFor(() => {
        expect(screen.getByText('Show all players')).toBeInTheDocument()
        expect(screen.getByText('Invalid query')).toBeInTheDocument()
      })
    })

    it('displays clear history button', async () => {
      renderHistory()

      await waitFor(() => {
        expect(screen.getByText(/clear history/i)).toBeInTheDocument()
      })
    })
  })

  describe('Search Functionality', () => {
    beforeEach(() => {
      mockUserMe.mockResolvedValue(mockUser)
      mockFetchHistory.mockResolvedValue({ items: mockQueries })
    })

    it('filters queries by search term', async () => {
      const user = userEvent.setup()
      renderHistory()

      await waitFor(() => {
        expect(screen.getByText('Show all players')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText(/search queries or sql/i)
      await user.type(searchInput, 'players')

      await waitFor(() => {
        expect(screen.getByText('Show all players')).toBeInTheDocument()
        expect(screen.queryByText('Invalid query')).not.toBeInTheDocument()
      })
    })

    it('shows no results message when search has no matches', async () => {
      const user = userEvent.setup()
      renderHistory()

      await waitFor(() => {
        expect(screen.getByText('Show all players')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText(/search queries or sql/i)
      await user.type(searchInput, 'nonexistent query')

      await waitFor(() => {
        expect(screen.getByText(/no matching queries found/i)).toBeInTheDocument()
      })
    })
  })

  describe('Status Filter', () => {
    beforeEach(() => {
      mockUserMe.mockResolvedValue(mockUser)
      mockFetchHistory.mockResolvedValue({ items: mockQueries })
    })

    it('filters queries by success status', async () => {
      const user = userEvent.setup()
      renderHistory()

      await waitFor(() => {
        expect(screen.getByText('Show all players')).toBeInTheDocument()
      })

      const filterSelect = screen.getByRole('combobox')
      await user.selectOptions(filterSelect, 'success')

      await waitFor(() => {
        expect(screen.getByText('Show all players')).toBeInTheDocument()
        expect(screen.queryByText('Invalid query')).not.toBeInTheDocument()
      })
    })

    it('filters queries by error status', async () => {
      const user = userEvent.setup()
      renderHistory()

      await waitFor(() => {
        expect(screen.getByText('Invalid query')).toBeInTheDocument()
      })

      const filterSelect = screen.getByRole('combobox')
      await user.selectOptions(filterSelect, 'error')

      await waitFor(() => {
        expect(screen.queryByText('Show all players')).not.toBeInTheDocument()
        expect(screen.getByText('Invalid query')).toBeInTheDocument()
      })
    })
  })

  describe('Clear History', () => {
    beforeEach(() => {
      mockUserMe.mockResolvedValue(mockUser)
      mockFetchHistory.mockResolvedValue({ items: mockQueries })
    })

    it('clears history when confirmed', async () => {
      const user = userEvent.setup()
      ;(globalThis.confirm as any).mockReturnValueOnce(true)
      mockClearHistory.mockResolvedValueOnce({})

      renderHistory()

      await waitFor(() => {
        expect(screen.getByText(/clear history/i)).toBeInTheDocument()
      })

      const clearButton = screen.getByText(/clear history/i).closest('button')
      if (clearButton) await user.click(clearButton)

      await waitFor(() => {
        expect(mockClearHistory).toHaveBeenCalled()
      })
    })

    it('does not clear history when cancelled', async () => {
      const user = userEvent.setup()
      ;(globalThis.confirm as any).mockReturnValueOnce(false)

      renderHistory()

      await waitFor(() => {
        expect(screen.getByText(/clear history/i)).toBeInTheDocument()
      })

      const clearButton = screen.getByText(/clear history/i).closest('button')
      if (clearButton) await user.click(clearButton)

      expect(mockClearHistory).not.toHaveBeenCalled()
    })
  })

  describe('Rerun Query', () => {
    beforeEach(() => {
      mockUserMe.mockResolvedValue(mockUser)
      mockFetchHistory.mockResolvedValue({ items: mockQueries })
    })

    it('navigates to interface page when rerun is clicked', async () => {
      const user = userEvent.setup()
      renderHistory()

      await waitFor(() => {
        expect(screen.getByText('Show all players')).toBeInTheDocument()
      })

      // Find the first history item card and hover to show rerun button
      const historyCards = screen.getAllByText('Show all players')[0].closest('div')
      if (historyCards) {
        const rerunButton = screen.getAllByText(/rerun/i)[0].closest('button')
        if (rerunButton) {
          await user.click(rerunButton)
          
          expect(mockNavigate).toHaveBeenCalledWith('/interface?question=Show%20all%20players')
        }
      }
    })
  })

  describe('Empty State', () => {
    beforeEach(() => {
      mockUserMe.mockResolvedValue(mockUser)
      mockFetchHistory.mockResolvedValue({ items: [] })
    })

    it('shows empty state when no queries exist', async () => {
      renderHistory()

      await waitFor(() => {
        expect(screen.getByText(/no queries yet/i)).toBeInTheDocument()
        expect(screen.getByText(/start by asking your first question/i)).toBeInTheDocument()
      })
    })

    it('navigates to interface page when start querying button is clicked', async () => {
      const user = userEvent.setup()
      renderHistory()

      await waitFor(() => {
        expect(screen.getByText(/start querying/i)).toBeInTheDocument()
      })

      const startButton = screen.getByText(/start querying/i).closest('button')
      if (startButton) {
        await user.click(startButton)
        expect(mockNavigate).toHaveBeenCalledWith('/interface')
      }
    })
  })
})

