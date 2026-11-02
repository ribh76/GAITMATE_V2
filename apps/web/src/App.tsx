import { useQuery } from '@tanstack/react-query'
import { Link, Route, Routes } from 'react-router-dom'
import { Button } from './components/Button'
import { getHealth } from './lib/api'

function Home() {
  const health = useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
    retry: false,
  })

  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <p className="text-sm font-semibold uppercase tracking-widest text-teal-700">
        Research demo
      </p>
      <h1 className="mt-4 text-4xl font-bold tracking-tight">GaitMate</h1>
      <p className="mt-4 max-w-prose text-lg text-slate-700">
        A foundation for ankle monitoring and clinician-directed rehabilitation.
        Sensor data and thresholds in this project are demonstrations, not
        clinical guidance.
      </p>
      <section
        aria-labelledby="api-status"
        className="mt-10 rounded-xl border border-slate-200 p-6"
      >
        <h2 id="api-status" className="font-semibold">
          Development API
        </h2>
        <p role="status" className="mt-2 text-slate-700">
          {health.isPending && 'Checking connection…'}
          {health.isError &&
            'API unavailable. Start the local development server.'}
          {health.isSuccess && `Connected to ${health.data.data.service}.`}
        </p>
      </section>
      <Button asChild className="mt-8">
        <Link to="/about">About this demo</Link>
      </Button>
    </main>
  )
}

function About() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <h1 className="text-3xl font-bold">About GaitMate</h1>
      <p className="mt-4">This is a nonclinical research demo.</p>
      <Link className="mt-6 inline-block text-teal-700 underline" to="/">
        Back
      </Link>
    </main>
  )
}

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/about" element={<About />} />
    </Routes>
  )
}
