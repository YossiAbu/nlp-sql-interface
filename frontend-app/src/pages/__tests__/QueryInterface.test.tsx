// src/pages/__tests__/QueryInterface.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import QueryInterface from '../QueryInterface'

// Mock API
vi.mock('@/lib/api', () => ({
  fetchQuery: vi.fn(),
}))

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}))

describe('QueryInterface Page', () => {
  let mockFetchQuery: any

  beforeEach(async () => {
    vi.clearAllMocks()
    // Get the mocked function
    const api = await import('@/lib/api')
    mockFetchQuery = api.fetchQuery as any
  })

  const renderQueryInterface = () => {
    return render(
      <BrowserRouter>
        <QueryInterface />
      </BrowserRouter>
    )
  }

  describe('Rendering', () => {
    it('renders the main heading', () => {
      const { container } = renderQueryInterface()
      
      // Check for the heading "Ask Your Database"
      expect(container.textContent).toMatch(/ask.*your.*database/i)
    })

    it('renders the description text', () => {
      renderQueryInterface()
      
      expect(screen.getByText(/transform natural-language questions/i)).toBeInTheDocument()
    })

    it('renders the QueryInput component', () => {
      renderQueryInterface()
      
      expect(screen.getByRole('textbox')).toBeInTheDocument()
    })

    it('renders feature highlights when idle', () => {
      renderQueryInterface()
      
      expect(screen.getByText(/natural-language input/i)).toBeInTheDocument()
      expect(screen.getByText(/instant results/i)).toBeInTheDocument()
      expect(screen.getByText(/query history/i)).toBeInTheDocument()
    })
  })

  describe('Query Submission', () => {
    it('submits a query and displays results', async () => {
      const user = userEvent.setup()
      mockFetchQuery.mockResolvedValueOnce({
        sql_query: 'SELECT * FROM players LIMIT 10',
        results: 'Top 10 players',
        raw_rows: [{ name: 'Messi', ovr: 93 }],
        execution_time: 150,
        status: 'success',
        created_date: '2024-01-15T10:30:00Z',
      })

      const { container } = renderQueryInterface()
      
      // Submit a query
      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Show top 10 players')
      
      const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement
      if (submitButton) await user.click(submitButton)
      
      // Wait for results to appear - check container text content
      await waitFor(() => {
        expect(container.textContent).toContain('Top 10 players')
      })
    })

    it('shows loading state during query execution', async () => {
      const user = userEvent.setup()
      let resolvePromise: any
      mockFetchQuery.mockImplementationOnce(() => 
        new Promise(resolve => {
          resolvePromise = resolve
        })
      )

      const { container } = renderQueryInterface()
      
      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Show players')
      
      const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement
      if (submitButton) await user.click(submitButton)
      
      // Check for loading state (button text changes to "Processing")
      await waitFor(() => {
        expect(screen.getByText(/processing/i)).toBeInTheDocument()
      })
      
      // Clean up - resolve the promise
      if (resolvePromise) {
        resolvePromise({
          sql_query: 'SELECT * FROM players',
          results: 'Results',
          raw_rows: [],
          execution_time: 100,
          status: 'success',
        })
      }
    })

    it('handles query errors gracefully', async () => {
      const user = userEvent.setup()
      mockFetchQuery.mockRejectedValueOnce(new Error('Query failed'))

      const { container } = renderQueryInterface()
      
      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Invalid query')
      
      const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement
      if (submitButton) await user.click(submitButton)
      
      // Wait for error message
      await waitFor(() => {
        expect(screen.getByText(/failed to process your question/i)).toBeInTheDocument()
      })
    })
  })

  describe('Feature Highlights', () => {
    it('hides feature highlights when query is submitted', async () => {
      const user = userEvent.setup()
      mockFetchQuery.mockResolvedValueOnce({
        sql_query: 'SELECT * FROM players',
        results: 'Results',
        raw_rows: [],
        execution_time: 100,
        status: 'success',
      })

      const { container } = renderQueryInterface()
      
      // Verify features are visible initially
      expect(screen.getByText(/natural-language input/i)).toBeInTheDocument()
      
      // Submit query
      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Show players')
      
      const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement
      if (submitButton) await user.click(submitButton)
      
      // Wait for results and verify features are hidden
      await waitFor(() => {
        expect(screen.queryByText(/natural-language input/i)).not.toBeInTheDocument()
      })
    })
  })

  describe('URL Parameters', () => {
    it('processes question from URL parameter on mount', async () => {
      // Mock window.location.search
      const originalLocation = window.location
      delete (window as any).location
      window.location = { ...originalLocation, search: '?question=Show%20all%20players' }

      mockFetchQuery.mockResolvedValueOnce({
        sql_query: 'SELECT * FROM players',
        results: 'All players',
        raw_rows: [],
        execution_time: 100,
        status: 'success',
      })

      renderQueryInterface()

      // Wait for the query to be processed
      await waitFor(() => {
        expect(mockFetchQuery).toHaveBeenCalledWith('Show all players')
      }, { timeout: 500 })

      // Restore original location
      window.location = originalLocation
    })
  })

  describe('Query Results Display', () => {
    it('displays SQL query in results', async () => {
      const user = userEvent.setup()
      mockFetchQuery.mockResolvedValueOnce({
        sql_query: 'SELECT * FROM players LIMIT 5',
        results: 'Top 5 players',
        raw_rows: [{ name: 'Messi', ovr: 93 }],
        execution_time: 120,
        status: 'success',
      })

      const { container } = renderQueryInterface()
      
      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Show top 5 players')
      
      const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement
      if (submitButton) await user.click(submitButton)
      
      await waitFor(() => {
        expect(container.textContent).toMatch(/SELECT[\s\S]*FROM[\s\S]*players/i)
      })
    })

    it('displays execution time', async () => {
      const user = userEvent.setup()
      mockFetchQuery.mockResolvedValueOnce({
        sql_query: 'SELECT * FROM players',
        results: 'Players',
        raw_rows: [],
        execution_time: 250,
        status: 'success',
      })

      const { container } = renderQueryInterface()
      
      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Show players')
      
      const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement
      if (submitButton) await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/250 ms/i)).toBeInTheDocument()
      })
    })

    it('displays results table when raw_rows exist', async () => {
      const user = userEvent.setup()
      mockFetchQuery.mockResolvedValueOnce({
        sql_query: 'SELECT * FROM players',
        results: 'Players',
        raw_rows: [
          { name: 'Messi', ovr: 93 },
          { name: 'Ronaldo', ovr: 92 },
        ],
        execution_time: 150,
        status: 'success',
      })

      const { container } = renderQueryInterface()
      
      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Show players')
      
      const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement
      if (submitButton) await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByRole('table')).toBeInTheDocument()
        expect(screen.getByText('Messi')).toBeInTheDocument()
        expect(screen.getByText('Ronaldo')).toBeInTheDocument()
      })
    })
  })
})

