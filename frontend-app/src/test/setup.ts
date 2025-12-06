// frontend-app/src/test/setup.ts
import '@testing-library/jest-dom'

// Mock matchMedia for components that use it
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
})

// Mock ResizeObserver
globalThis.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

// Mock IntersectionObserver
globalThis.IntersectionObserver = class IntersectionObserver {
  root: Element | Document | null = null
  rootMargin = ''
  thresholds: number[] = []
  
  constructor(
    callback: IntersectionObserverCallback,
    options?: IntersectionObserverInit
  ) {
    this.root = options?.root ?? null
    this.rootMargin = options?.rootMargin ?? ''
    this.thresholds = Array.isArray(options?.threshold) 
      ? options.threshold 
      : options?.threshold !== undefined 
      ? [options.threshold] 
      : []
  }
  
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords() { return [] }
} as any

