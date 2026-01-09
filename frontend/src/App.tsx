import { useState, useEffect } from 'react'
import './App.css'
import { healthCheck } from './services/api'

function App() {
  const [health, setHealth] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await healthCheck()
        setHealth(response)
      } catch (error) {
        console.error('Failed to fetch health:', error)
      } finally {
        setLoading(false)
      }
    }
    checkHealth()
  }, [])

  return (
    <div className="App">
      <header className="App-header">
        <h1>FAANG Interview Simulation System</h1>
        <p>AI-driven interview simulation with realistic FAANG-style interviews</p>
        
        <div className="status-card">
          <h2>System Status</h2>
          {loading ? (
            <p>Checking system health...</p>
          ) : health ? (
            <div>
              <p className="status-ok">✓ Backend Connected</p>
              <p>Service: {health.service}</p>
              <p>Status: {health.status}</p>
            </div>
          ) : (
            <p className="status-error">✗ Backend Unavailable</p>
          )}
        </div>

        <div className="info-card">
          <h2>Phase 0 & 1 Complete</h2>
          <ul style={{ textAlign: 'left' }}>
            <li>✓ Repository structure established</li>
            <li>✓ FastAPI backend with health endpoint</li>
            <li>✓ React frontend with Vite</li>
            <li>✓ Core data models (JobProfile, Candidate, PipelineRun, StageResult)</li>
            <li>✓ Pipeline planner skeleton</li>
            <li>✓ POST /pipeline/start endpoint</li>
            <li>✓ Stage state machine implemented</li>
          </ul>
        </div>
      </header>
    </div>
  )
}

export default App
