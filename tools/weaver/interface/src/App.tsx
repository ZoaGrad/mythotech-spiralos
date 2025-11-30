import { useState, useEffect } from 'react'
import './App.css'

interface Status {
  status: string
  git: { branch: string; dirty: boolean; root: string }
  supabase: { connected: boolean }
  ai: { ready: boolean; context_loaded: boolean }
}

function App() {
  const [status, setStatus] = useState<Status | null>(null)
  const [input, setInput] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch('/api/status')
      .then(res => res.json())
      .then(data => setStatus(data))
      .catch(err => console.error(err))
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input) return
    setLoading(true)
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      })
      const data = await res.json()
      setResponse(data.response)
    } catch (err) {
      console.error(err)
      setResponse('Error connecting to Weaver.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header className="status-bar">
        <div className="status-item">
          <span className="label">SYSTEM:</span>
          <span className={`value ${status?.status === 'ONLINE' ? 'green' : 'red'}`}>
            {status?.status || 'OFFLINE'}
          </span>
        </div>
        <div className="status-item">
          <span className="label">GIT:</span>
          <span className="value">{status?.git.branch || 'Unknown'}</span>
          {status?.git.dirty && <span className="dirty-flag">*</span>}
        </div>
        <div className="status-item">
          <span className="label">DB:</span>
          <span className={`value ${status?.supabase.connected ? 'green' : 'red'}`}>
            {status?.supabase.connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <div className="status-item">
          <span className="label">AI:</span>
          <span className={`value ${status?.ai.ready ? 'green' : 'red'}`}>
            {status?.ai.ready ? 'Ready' : 'Offline'}
          </span>
        </div>
      </header>

      <main className="terminal">
        <div className="output">
          {response && <div className="response">{response}</div>}
        </div>
        <form onSubmit={handleSubmit} className="input-line">
          <span className="prompt">&gt;</span>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter command..."
            disabled={loading}
            autoFocus
          />
        </form>
      </main>
    </div>
  )
}

export default App
