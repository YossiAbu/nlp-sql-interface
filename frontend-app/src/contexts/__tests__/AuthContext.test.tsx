// src/contexts/__tests__/AuthContext.test.tsx
import { render, screen, act, renderHook } from '@testing-library/react'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { AuthProvider, useAuth, User } from '../AuthContext'


describe('AuthContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
  })

  describe('AuthProvider', () => {
    it('provides auth context to children', () => {
      render(
        <AuthProvider>
          <div>Test Child</div>
        </AuthProvider>
      )
      
      expect(screen.getByText('Test Child')).toBeInTheDocument()
    })

    it('initializes with null user when localStorage is empty', () => {
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })
      
      expect(result.current.user).toBeNull()
    })

    it('loads user from localStorage on mount', () => {
      const mockUser: User = {
        id: '123',
        name: 'Test User',
        email: 'test@example.com',
      }
      
      localStorage.setItem('demo-auth-user', JSON.stringify(mockUser))
      
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })
      
      expect(result.current.user).toEqual(mockUser)
    })
  })

  describe('login', () => {
    it('sets user and saves to localStorage', () => {
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })
      
      const mockUser: User = {
        id: '456',
        name: 'John Doe',
        email: 'john@example.com',
      }
      
      act(() => {
        result.current.login(mockUser)
      })
      
      expect(result.current.user).toEqual(mockUser)
      expect(localStorage.getItem('demo-auth-user')).toBe(JSON.stringify(mockUser))
    })
  })

  describe('logout', () => {
    it('clears user and removes from localStorage', () => {
      const mockUser: User = {
        id: '789',
        name: 'Jane Smith',
        email: 'jane@example.com',
      }
      
      localStorage.setItem('demo-auth-user', JSON.stringify(mockUser))
      
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })
      
      act(() => {
        result.current.logout()
      })
      
      expect(result.current.user).toBeNull()
      expect(localStorage.getItem('demo-auth-user')).toBeNull()
    })
  })

  describe('useAuth hook', () => {
    it('throws error when used outside AuthProvider', () => {
      // Suppress console.error for this test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      expect(() => {
        renderHook(() => useAuth())
      }).toThrow('useAuth must be used within an AuthProvider')
      
      consoleSpy.mockRestore()
    })
  })
})

