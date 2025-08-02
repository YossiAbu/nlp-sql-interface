export const createPageUrl = (page: string, params?: Record<string, string>) => {
  const query = new URLSearchParams(params).toString()
  return `/${page}${query ? `?${query}` : ''}`
}
