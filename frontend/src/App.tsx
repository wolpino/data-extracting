import { useEffect, useState } from 'react'
import './App.css'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type HealthState =
  | { status: 'loading' }
  | { status: 'ok'; message: string }
  | { status: 'error'; message: string }

function App() {
  const [health, setHealth] = useState<HealthState>({ status: 'loading' })

  useEffect(() => {
    const controller = new AbortController()

    async function checkHealth() {
      try {
        const response = await fetch(`${apiBaseUrl}/api/v1/health`, {
          signal: controller.signal,
        })
        if (!response.ok) {
          setHealth({
            status: 'error',
            message: `Health check failed (${response.status})`,
          })
          return
        }
        const body = (await response.json()) as { status?: string }
        setHealth({
          status: 'ok',
          message: `API ${body.status ?? 'ok'} at ${apiBaseUrl}`,
        })
      } catch (error) {
        if (controller.signal.aborted) return
        const message =
          error instanceof Error ? error.message : 'Unable to reach API'
        setHealth({ status: 'error', message })
      }
    }

    void checkHealth()
    return () => controller.abort()
  }, [])

  return (
    <main className="app">
      <h1>Orders</h1>
      <p className="muted">Coming soon — scaffold only (PR1).</p>
      <p>
        <span className="label">API base:</span> <code>{apiBaseUrl}</code>
      </p>
      <p>
        <span className="label">Health:</span>{' '}
        {health.status === 'loading' && 'Checking…'}
        {health.status === 'ok' && <span className="ok">{health.message}</span>}
        {health.status === 'error' && (
          <span className="error">{health.message}</span>
        )}
      </p>
      <p className="muted">
        Browser health may fail until CORS lands in PR3; API curl still works in
        PR1.
      </p>
    </main>
  )
}

export default App
