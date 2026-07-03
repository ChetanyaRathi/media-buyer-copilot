import { useState } from 'react'
import { analyze, analyzeSample } from './api.js'
import UploadZone from './components/UploadZone.jsx'
import PipelineStatus from './components/PipelineStatus.jsx'
import VerdictBanner from './components/VerdictBanner.jsx'
import DecisionsTable from './components/DecisionsTable.jsx'
import ChatBox from './components/ChatBox.jsx'

export default function App() {
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  async function run(loader) {
    setStatus('processing')
    setError('')
    try {
      const data = await loader()
      setResult(data)
      setStatus('done')
    } catch (e) {
      setError(e.message || 'Something went wrong.')
      setStatus('idle')
    }
  }

  const onFiles = (files) => { if (files && files.length) run(() => analyze(files)) }
  const onSample = () => run(() => analyzeSample())
  const reset = () => { setResult(null); setStatus('idle'); setError('') }

  return (
    <div className="wrap">
      <div className="topbar">
        <div className="brand">media<span>·</span>buyer copilot</div>
        <div className="tag">Reads your Meta / Google / TikTok / Taboola spend and tells you what to scale, kill, and watch — with the reasoning behind every call.</div>
      </div>

      {status === 'idle' && <UploadZone onFiles={onFiles} onSample={onSample} error={error} />}
      {status === 'processing' && <PipelineStatus />}
      {status === 'done' && result && (
        <div className="fade">
          <VerdictBanner summary={result.summary} />
          <DecisionsTable decisions={result.decisions} metrics={result.metrics} />
          <ChatBox context={result} />
          <div style={{ marginTop: 28 }}>
            <button className="btn ghost small" onClick={reset}>New analysis</button>
          </div>
        </div>
      )}
    </div>
  )
}
