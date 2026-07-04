import { useState, useEffect } from 'react'
import { analyze, analyzeSample, health } from './api.js'
import UploadZone from './components/UploadZone.jsx'
import PipelineStatus from './components/PipelineStatus.jsx'
import VerdictBanner from './components/VerdictBanner.jsx'
import DecisionsTable from './components/DecisionsTable.jsx'
import ChatBox from './components/ChatBox.jsx'

function LiveStatus({ onModelUpdate }) {
  const [status, setStatus] = useState('loading') // loading, live, offline
  const [info, setInfo] = useState(null)

  useEffect(() => {
    let mounted = true
    health()
      .then(res => {
        if (!mounted) return
        setInfo(res)
        setStatus('live')
        if (onModelUpdate) onModelUpdate(res.model)
      })
      .catch(() => {
        if (!mounted) return
        setStatus('offline')
      })
    return () => { mounted = false }
  }, [onModelUpdate])

  let dotClass = 'loading'
  let text = 'Connecting'
  if (status === 'live') {
    dotClass = 'live'
    text = info?.provider === 'ollama' ? `Live · Local · ${info?.model || 'model'}` : 'Live'
  } else if (status === 'offline') {
    dotClass = 'offline'
    text = 'Backend offline'
  }

  return (
    <div className="status-chip-container">
      <div className="status-pill">
        <span className={`status-dot ${dotClass}`}></span>
        {text}
      </div>
      <div className="tag">Reads your Meta / Google / TikTok / Taboola spend and tells you what to scale, kill, and watch — with the reasoning behind every call.</div>
    </div>
  )
}

export default function App() {
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [liveModel, setLiveModel] = useState('Unknown')

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
      <div className="topbar fade">
        <div className="brand-container">
          <div className="logo-mark">
            <div className="logo-bar red"></div>
            <div className="logo-bar amber"></div>
            <div className="logo-bar green"></div>
          </div>
          <div className="brand-text-block">
            <div className="brand">media<span>·</span>buyer copilot</div>
            <div className="brand-sub">Ad-spend decision engine</div>
          </div>
        </div>
        <LiveStatus onModelUpdate={setLiveModel} />
      </div>

      {status === 'idle' && <UploadZone onFiles={onFiles} onSample={onSample} error={error} />}
      {status === 'processing' && <PipelineStatus />}
      {status === 'done' && result && (
        <div className="fade fade-delay-1">
          <VerdictBanner summary={result.summary} />
          <DecisionsTable decisions={result.decisions} metrics={result.metrics} />
          <ChatBox context={result} />
          <div style={{ marginTop: 28, textAlign: 'center' }}>
            <button className="btn ghost" onClick={reset}>New analysis</button>
          </div>
        </div>
      )}
      
      <footer className="fade fade-delay-3">
        <div>Built by <a href="https://github.com/ChetanyaRathi/media-buyer-copilot" target="_blank" rel="noreferrer">Chetanya Rathi</a> · media-buyer-copilot</div>
      </footer>
    </div>
  )
}
