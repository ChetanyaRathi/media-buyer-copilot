import { useRef, useState } from 'react'

export default function UploadZone({ onFiles, onSample, error }) {
  const inputRef = useRef(null)
  const [hot, setHot] = useState(false)

  const drop = (e) => {
    e.preventDefault()
    setHot(false)
    onFiles(Array.from(e.dataTransfer.files || []))
  }

  return (
    <div className="fade">
      <div
        className={`drop${hot ? ' hot' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setHot(true) }}
        onDragLeave={() => setHot(false)}
        onDrop={drop}
      >
        <div className="micro">Step 1</div>
        <h2>Drop an ad export — CSV or XLSX</h2>
        <p>Meta, Google, TikTok, or Taboola. Real, messy exports welcome.</p>
        <div className="row-actions">
          <button className="btn" onClick={() => inputRef.current.click()}>Choose file</button>
          <button className="btn ghost" onClick={onSample}>Try it with sample data</button>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          multiple
          style={{ display: 'none' }}
          onChange={(e) => onFiles(Array.from(e.target.files || []))}
        />
      </div>
      {error && <div className="err">{error}</div>}
    </div>
  )
}
