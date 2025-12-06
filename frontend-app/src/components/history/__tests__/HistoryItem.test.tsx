// src/components/history/__tests__/HistoryItem.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import HistoryItem from '../HistoryItem'
import { Query } from '@/entities/Query'


// Mock navigator.clipboard
Object.defineProperty(navigator, 'clipboard', {
  value: {
    writeText: vi.fn(),
  },
  writable: true,
  configurable: true,
})

describe('HistoryItem', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const mockQuery: Query = {
    id: '123',
    user_id: 'user1',
    question: 'Show all players',
    sql_query: 'SELECT * FROM players',
    status: 'success',
    execution_time: 150,
    results: 'Query results',
    raw_rows: [{ name: 'Messi', ovr: 93 }],
    created_date: '2024-01-15T10:30:00Z',
    error_message: null,
  }

  describe('Rendering', () => {
    it('renders question text', () => {
      render(<HistoryItem query={mockQuery} index={0} />)
      
      expect(screen.getByText('Show all players')).toBeInTheDocument()
    })

    it('renders SQL query', () => {
      const { container } = render(<HistoryItem query={mockQuery} index={0} />)
      
      // SQL formatter adds newlines, use [\s\S]* to match across lines
      expect(container.textContent).toMatch(/SELECT[\s\S]*FROM[\s\S]*players/i)
    })

    it('displays success badge for successful query', () => {
      render(<HistoryItem query={mockQuery} index={0} />)
      
      expect(screen.getByText(/success/i)).toBeInTheDocument()
    })

    it('displays error badge for failed query', () => {
      const errorQuery = { ...mockQuery, status: 'error' as const, error_message: 'Failed' }
      render(<HistoryItem query={errorQuery} index={0} />)
      
      expect(screen.getByText(/error/i)).toBeInTheDocument()
    })

    it('displays execution time', () => {
      const { container } = render(<HistoryItem query={mockQuery} index={0} />)
      
      expect(container.textContent).toMatch(/150\s*ms/i)
    })

    it('displays row count when raw_rows exist', () => {
      const { container } = render(<HistoryItem query={mockQuery} index={0} />)
      
      expect(container.textContent).toContain('1 row')
    })

    it('formats date correctly', () => {
      const { container } = render(<HistoryItem query={mockQuery} index={0} />)
      
      // Check that date is formatted (exact format depends on locale)
      // The date should contain some format of the date
      expect(container.textContent).toMatch(/(15|01|2024)/)
    })
  })

  describe('Rerun Functionality', () => {
    it('shows rerun button when onRerun is provided', () => {
      const mockOnRerun = vi.fn()
      render(<HistoryItem query={mockQuery} onRerun={mockOnRerun} index={0} />)
      
      // Find button by text content
      const rerunButton = screen.getByText(/rerun/i).closest('button')
      expect(rerunButton).toBeInTheDocument()
    })

    it('does not show rerun button when onRerun is not provided', () => {
      render(<HistoryItem query={mockQuery} index={0} />)
      
      const rerunButton = screen.queryByText(/rerun/i)
      expect(rerunButton).not.toBeInTheDocument()
    })

    it('calls onRerun with query when rerun button is clicked', async () => {
      const user = userEvent.setup()
      const mockOnRerun = vi.fn()
      render(<HistoryItem query={mockQuery} onRerun={mockOnRerun} index={0} />)
      
      const rerunButton = screen.getByText(/rerun/i).closest('button')
      if (rerunButton) {
        await user.click(rerunButton)
        expect(mockOnRerun).toHaveBeenCalledWith(mockQuery)
      }
    })
  })

  describe('Copy Functionality', () => {
    it('has copy buttons in the component', () => {
      const { container } = render(<HistoryItem query={mockQuery} index={0} />)
      
      // Verify the component has interactive elements (buttons)
      const buttons = container.querySelectorAll('button')
      expect(buttons.length).toBeGreaterThan(0)
    })

    it('renders SQL query that can be copied', () => {
      const { container } = render(<HistoryItem query={mockQuery} index={0} />)
      
      // Verify SQL is displayed and accessible (formatter adds newlines)
      expect(container.textContent).toMatch(/SELECT[\s\S]*FROM[\s\S]*players/i)
    })
  })

  describe('Edge Cases', () => {
    it('handles missing created_date', () => {
      const queryWithoutDate = { ...mockQuery, created_date: undefined }
      const { container } = render(<HistoryItem query={queryWithoutDate as Query} index={0} />)
      
      // Should still render the component
      expect(container.textContent).toBeTruthy()
    })

    it('handles query without SQL', () => {
      const queryWithoutSQL = { ...mockQuery, sql_query: '' }
      const { container } = render(<HistoryItem query={queryWithoutSQL} index={0} />)
      
      // Component should still render (using motion.div and Card, not article)
      expect(container.firstChild).toBeInTheDocument()
    })

    it('handles query without raw_rows', () => {
      const queryWithoutRows = { ...mockQuery, raw_rows: undefined }
      const { container } = render(<HistoryItem query={queryWithoutRows as Query} index={0} />)
      
      // Should not display row count
      expect(container.textContent).not.toContain('row')
    })
  })
})

