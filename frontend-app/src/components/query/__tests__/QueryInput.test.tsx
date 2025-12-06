// src/components/query/__tests__/QueryInput.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import QueryInput from '../QueryInput'


describe('QueryInput', () => {
  const mockOnSubmit = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders the form with textarea', () => {
      const { container } = render(<QueryInput onSubmit={mockOnSubmit} isLoading={false} />)
      
      expect(screen.getByRole('textbox')).toBeInTheDocument()
      // Check that submit button exists (type="submit")
      const submitButton = container.querySelector('button[type="submit"]')
      expect(submitButton).toBeInTheDocument()
    })

    it('displays placeholder questions', () => {
      render(<QueryInput onSubmit={mockOnSubmit} isLoading={false} />)
      
      expect(screen.getByText(/try these example questions/i)).toBeInTheDocument()
      expect(screen.getByText(/show me the top 10 players by overall rating/i)).toBeInTheDocument()
    })
  })

  describe('Form Submission', () => {
    it('calls onSubmit with question when form is submitted', async () => {
      const user = userEvent.setup()
      const { container } = render(<QueryInput onSubmit={mockOnSubmit} isLoading={false} />)
      
      await user.type(screen.getByRole('textbox'), 'Show all players')
      
      const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement
      if (submitButton) await user.click(submitButton)
      
      expect(mockOnSubmit).toHaveBeenCalledWith('Show all players')
    })

    it('clears input after submission', async () => {
      const user = userEvent.setup()
      const { container } = render(<QueryInput onSubmit={mockOnSubmit} isLoading={false} />)
      
      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Show all players')
      
      const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement
      if (submitButton) await user.click(submitButton)
      
      expect(textarea).toHaveValue('')
    })

    it('trims whitespace from question', async () => {
      const user = userEvent.setup()
      const { container } = render(<QueryInput onSubmit={mockOnSubmit} isLoading={false} />)
      
      await user.type(screen.getByRole('textbox'), '  Show all players  ')
      
      const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement
      if (submitButton) await user.click(submitButton)
      
      expect(mockOnSubmit).toHaveBeenCalledWith('Show all players')
    })

    it('does not submit empty question', async () => {
      const user = userEvent.setup()
      const { container } = render(<QueryInput onSubmit={mockOnSubmit} isLoading={false} />)
      
      const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement
      if (submitButton) await user.click(submitButton)
      
      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('does not submit whitespace-only question', async () => {
      const user = userEvent.setup()
      const { container } = render(<QueryInput onSubmit={mockOnSubmit} isLoading={false} />)
      
      await user.type(screen.getByRole('textbox'), '   ')
      
      const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement
      if (submitButton) await user.click(submitButton)
      
      expect(mockOnSubmit).not.toHaveBeenCalled()
    })
  })

  describe('Loading State', () => {
    it('disables textarea when loading', () => {
      render(<QueryInput onSubmit={mockOnSubmit} isLoading={true} />)
      
      expect(screen.getByRole('textbox')).toBeDisabled()
    })

    it('disables submit button when loading', () => {
      render(<QueryInput onSubmit={mockOnSubmit} isLoading={true} />)
      
      const submitButton = screen.getByRole('button', { name: /processing/i })
      expect(submitButton).toBeDisabled()
    })

    it('shows processing text when loading', () => {
      render(<QueryInput onSubmit={mockOnSubmit} isLoading={true} />)
      
      expect(screen.getByText(/processing/i)).toBeInTheDocument()
    })

    it('disables example buttons when loading', () => {
      render(<QueryInput onSubmit={mockOnSubmit} isLoading={true} />)
      
      // Get all buttons and check if example buttons are disabled
      const allButtons = screen.getAllByRole('button')
      // At least the submit button should be disabled
      expect(allButtons.some(btn => btn.disabled)).toBe(true)
    })
  })

  describe('Example Questions', () => {
    it('fills textarea when example button is clicked', async () => {
      const user = userEvent.setup()
      render(<QueryInput onSubmit={mockOnSubmit} isLoading={false} />)
      
      await user.click(screen.getByText(/show me the top 10 players by overall rating/i))
      
      expect(screen.getByRole('textbox')).toHaveValue('Show me the top 10 players by overall rating')
    })

    it('does not fill textarea when loading', async () => {
      const user = userEvent.setup()
      render(<QueryInput onSubmit={mockOnSubmit} isLoading={true} />)
      
      const exampleButton = screen.getByText(/show me the top 10 players by overall rating/i)
      await user.click(exampleButton)
      
      expect(screen.getByRole('textbox')).toHaveValue('')
    })
  })

  describe('Button State', () => {
    it('disables submit button when input is empty', () => {
      const { container } = render(<QueryInput onSubmit={mockOnSubmit} isLoading={false} />)
      
      const submitButton = container.querySelector('button[type="submit"]')
      expect(submitButton).toBeDisabled()
    })

    it('enables submit button when input has text', async () => {
      const user = userEvent.setup()
      const { container } = render(<QueryInput onSubmit={mockOnSubmit} isLoading={false} />)
      
      await user.type(screen.getByRole('textbox'), 'Show players')
      
      const submitButton = container.querySelector('button[type="submit"]')
      expect(submitButton).not.toBeDisabled()
    })
  })
})

