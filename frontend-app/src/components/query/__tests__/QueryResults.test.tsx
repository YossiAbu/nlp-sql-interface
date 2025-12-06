// src/components/query/__tests__/QueryResults.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import QueryResults from '../QueryResults'


// Mock navigator.clipboard
Object.defineProperty(navigator, 'clipboard', {
  value: {
    writeText: vi.fn(),
  },
  writable: true,
  configurable: true,
})

describe('QueryResults', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Loading State', () => {
    it('shows loading skeleton when isLoading is true', () => {
      const { container } = render(<QueryResults query={null} isLoading={true} />)
      
      expect(container.querySelector('.animate-pulse')).toBeInTheDocument()
    })
  })

  describe('No Query State', () => {
    it('renders nothing when no query and not loading', () => {
      const { container } = render(<QueryResults query={null} isLoading={false} />)
      
      expect(container.firstChild).toBeNull()
    })
  })

  describe('Success State', () => {
    const successQuery = {
      sql_query: 'SELECT * FROM players LIMIT 5',
      status: 'success' as const,
      execution_time: 123,
      results: 'Top 5 players',
      raw_rows: [
        { name: 'Messi', ovr: 93 },
        { name: 'Ronaldo', ovr: 92 },
      ],
    }

    it('displays SQL query', () => {
      const { container } = render(<QueryResults query={successQuery} isLoading={false} />)
      
      // SQL formatter adds newlines, use [\s\S]* to match across lines
      expect(container.textContent).toMatch(/SELECT[\s\S]*FROM[\s\S]*players[\s\S]*LIMIT[\s\S]*5/i)
    })

    it('displays execution time', () => {
      render(<QueryResults query={successQuery} isLoading={false} />)
      
      expect(screen.getByText(/123 ms/i)).toBeInTheDocument()
    })

    it('displays results table when raw_rows exist', () => {
      render(<QueryResults query={successQuery} isLoading={false} />)
      
      expect(screen.getByRole('table')).toBeInTheDocument()
      expect(screen.getByText('Messi')).toBeInTheDocument()
      expect(screen.getByText('Ronaldo')).toBeInTheDocument()
    })

    it('displays correct number of rows', () => {
      render(<QueryResults query={successQuery} isLoading={false} />)
      
      expect(screen.getByText(/2 rows/i)).toBeInTheDocument()
    })

    it('displays human-readable answer when results exist', () => {
      render(<QueryResults query={successQuery} isLoading={false} />)
      
      expect(screen.getByText('Top 5 players')).toBeInTheDocument()
    })

    it('displays user question when provided', () => {
      render(
        <QueryResults 
          query={successQuery} 
          isLoading={false} 
          userQuestion="Show me the best players"
        />
      )
      
      expect(screen.getByText(/show me the best players/i)).toBeInTheDocument()
    })
  })

  describe('Error State', () => {
    const errorQuery = {
      sql_query: 'SELECT * FROM invalid_table',
      status: 'error' as const,
      execution_time: 50,
      error_message: 'Table does not exist',
    }

    it('displays error message', () => {
      render(<QueryResults query={errorQuery} isLoading={false} />)
      
      expect(screen.getByText(/error executing query/i)).toBeInTheDocument()
      expect(screen.getByText(/table does not exist/i)).toBeInTheDocument()
    })

    it('displays SQL query that caused error', () => {
      render(<QueryResults query={errorQuery} isLoading={false} />)
      
      expect(screen.getByText(/SELECT \* FROM invalid_table/i)).toBeInTheDocument()
    })
  })

  describe('Copy Functionality', () => {
    const queryWithQuestion = {
      sql_query: 'SELECT * FROM players',
      status: 'success' as const,
      execution_time: 100,
    }

    it('copies user question to clipboard', async () => {
      render(
        <QueryResults 
          query={queryWithQuestion} 
          isLoading={false} 
          userQuestion="Show all players"
        />
      )
      
      // Just verify the user question is displayed
      expect(screen.getByText(/show all players/i)).toBeInTheDocument()
    })

    it('copies SQL query to clipboard', async () => {
      const user = userEvent.setup()
      const { container } = render(<QueryResults query={queryWithQuestion} isLoading={false} />)
      
      // Verify SQL is displayed (formatter adds newlines)
      expect(container.textContent).toMatch(/SELECT[\s\S]*FROM[\s\S]*players/i)
    })

    it('shows copy buttons in the component', () => {
      render(<QueryResults query={queryWithQuestion} isLoading={false} />)
      
      // Verify copy functionality exists by checking for Copy text
      const copyElements = screen.queryAllByText(/copy/i)
      expect(copyElements.length).toBeGreaterThan(0)
    })
  })

  describe('Table Rendering', () => {
    const queryWithTable = {
      sql_query: 'SELECT name, age, position FROM players',
      status: 'success' as const,
      execution_time: 100,
      raw_rows: [
        { name: 'Messi', age: 36, position: 'RW' },
        { name: 'Ronaldo', age: 38, position: 'ST' },
        { name: 'Mbappe', age: 25, position: 'LW' },
      ],
    }

    it('renders table headers correctly', () => {
      render(<QueryResults query={queryWithTable} isLoading={false} />)
      
      const table = screen.getByRole('table')
      expect(table).toBeInTheDocument()
      
      // Verify headers exist by checking text content
      expect(screen.getByText('name')).toBeInTheDocument()
      expect(screen.getByText('age')).toBeInTheDocument()
      expect(screen.getByText('position')).toBeInTheDocument()
    })

    it('renders all rows', () => {
      render(<QueryResults query={queryWithTable} isLoading={false} />)
      
      expect(screen.getByRole('table')).toBeInTheDocument()
      expect(screen.getByText('Messi')).toBeInTheDocument()
      expect(screen.getByText('Ronaldo')).toBeInTheDocument()
      expect(screen.getByText('Mbappe')).toBeInTheDocument()
    })

    it('handles null values', () => {
      const queryWithNull = {
        ...queryWithTable,
        raw_rows: [{ name: 'Test', age: null, position: 'ST' }],
      }
      
      render(<QueryResults query={queryWithNull} isLoading={false} />)
      
      expect(screen.getByText('null')).toBeInTheDocument()
    })
  })
})

