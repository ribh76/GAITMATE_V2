import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { expect, test } from 'vitest'
import { App } from './App'

test('shows the demo status and route', () => {
  render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter initialEntries={['/about']}>
        <App />
      </MemoryRouter>
    </QueryClientProvider>,
  )
  expect(
    screen.getByRole('heading', { name: 'About GaitMate' }),
  ).toBeInTheDocument()
  expect(screen.getByRole('link', { name: 'Back' })).toHaveAttribute(
    'href',
    '/',
  )
})
