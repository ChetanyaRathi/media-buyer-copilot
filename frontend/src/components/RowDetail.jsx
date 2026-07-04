import { useState } from 'react'

const num = (v, d = 2) => (v === null || v === undefined ? '—' : Number(v).toFixed(d))

export default function RowDetail({ decision, metric }) {
  const [copied, setCopied] = useState(false)

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(decision.mcp_payload, null, 2))
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch (e) {
      void e
    }
  }

  const cells = [
    ['Spend', metric.spend != null ? `$${Math.round(metric.spend).toLocaleString()}` : '—'],
    ['Revenue', metric.revenue != null ? `$${Math.round(metric.revenue).toLocaleString()}` : '—'],
    ['Impressions', metric.impressions != null ? metric.impressions.toLocaleString() : '—'],
    ['Clicks', metric.clicks != null ? metric.clicks.toLocaleString() : '—'],
    ['Conversions', num(metric.conversions, 0)],
    ['CTR', metric.ctr != null ? `${metric.ctr}%` : '—'],
    ['CVR', metric.cvr != null ? `${metric.cvr}%` : '—'],
    ['EPC', metric.epc != null ? `$${metric.epc}` : '—'],
    ['Days', metric.days ?? '—']
  ]

  return (
    <div>
      <div className="reason">{decision.reasoning}</div>
      {decision.critique_note && <div className="note">Verifier: {decision.critique_note}</div>}
      <div className="grid">
        {cells.map(([k, v]) => (
          <div key={k}><div className="k">{k}</div><div className="v">{v}</div></div>
        ))}
      </div>
      <div className="draft">
        <div className="draft-action">
          <svg className="bolt" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
          </svg>
          <span>{decision.drafted_action}</span>
        </div>
        <button className="btn ghost small" onClick={copy}>{copied ? 'Copied' : 'Copy MCP payload'}</button>
      </div>
    </div>
  )
}
