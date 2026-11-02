import { Slot } from '@radix-ui/react-slot'
import type { ButtonHTMLAttributes } from 'react'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  asChild?: boolean
}

export function Button({
  asChild = false,
  className = '',
  ...props
}: ButtonProps) {
  const Component = asChild ? Slot : 'button'
  return (
    <Component
      className={`inline-flex min-h-10 items-center justify-center rounded-md bg-teal-700 px-4 py-2 font-medium text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700 disabled:opacity-50 ${className}`}
      {...props}
    />
  )
}
