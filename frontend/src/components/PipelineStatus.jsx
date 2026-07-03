import { useEffect, useState } from 'react'

const STAGES = [
  'Ingesting exports',
  'Normalizing columns',
  'Computing metrics',
  'Analyzing performance',
  'Verifying recommendations'
]

export default function PipelineStatus() {
  const [active, setActive] = useState(0)
  useEffect(() => {
    const timer = setInterval(() => {
      setActive((current) => (current < STAGES.length - 1 ? current + 1 : current))
    }, 1200)
    return () => clearInterval(timer)
  }, [])
  return (
    <div className="stages fade">
      <div className="micro">Running the pipeline</div>
      {STAGES.map((label, index) => (
        <div
          key={label}
          className={`stage${index === active ? ' active' : ''}${index < active ? ' done' : ''}`}
        >
          <span className="dot" />
          {label}
        </div>
      ))}
    </div>
  )
}
