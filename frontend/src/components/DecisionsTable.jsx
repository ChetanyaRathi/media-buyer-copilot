import { Fragment, useState } from 'react'
import RowDetail from './RowDetail.jsx'
import PlatformBadge from './PlatformBadge.jsx'

const keyOf = (r) => `${r.platform}|${r.campaign}|${r.ad_set}`
const num = (v, d = 2) => (v === null || v === undefined ? '—' : Number(v).toFixed(d))
const money = (v) => (v === null || v === undefined ? '—' : `$${Math.round(v).toLocaleString()}`)

export default function DecisionsTable({ decisions, metrics }) {
  const metricMap = {}
  for (const m of metrics) metricMap[keyOf(m)] = m
  const platforms = ['all', ...Array.from(new Set(decisions.map((d) => d.platform)))]

  const [platform, setPlatform] = useState('all')
  const [decision, setDecision] = useState('all')
  const [open, setOpen] = useState(null)

  const rows = decisions.filter(
    (d) => (platform === 'all' || d.platform === platform) && (decision === 'all' || d.decision === decision)
  )

  const trend = (v) => {
    if (v === null || v === undefined) return <span className="sub">—</span>
    const cls = v > 2 ? 'pos' : v < -2 ? 'neg' : ''
    return <span className={cls}>{v > 0 ? '+' : ''}{v}%</span>
  }

  return (
    <div className="fade fade-delay-2">
      <div className="section-head">
        <div className="micro">Recommendations · {rows.length}</div>
        <div className="filters">
          {['all', 'scale', 'kill', 'watch'].map((d) => (
            <button key={d} className={`chip${decision === d ? ' on' : ''}`} onClick={() => setDecision(d)}>{d}</button>
          ))}
          <select className="chip" value={platform} onChange={(e) => setPlatform(e.target.value)}>
            {platforms.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
      </div>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Platform</th>
              <th>Campaign / Ad set</th>
              <th className="n">Spend</th>
              <th className="n">ROAS</th>
              <th className="n">CPA</th>
              <th className="n">EPC</th>
              <th className="n">3d trend</th>
              <th>Call</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((d) => {
              const m = metricMap[keyOf(d)] || {}
              const k = keyOf(d)
              return (
                <Fragment key={k}>
                  <tr onClick={() => setOpen(open === k ? null : k)}>
                    <td><PlatformBadge platform={d.platform} /></td>
                    <td><div className="name">{d.ad_set}</div><div className="sub">{d.campaign}</div></td>
                    <td className="n">{money(m.spend)}</td>
                    <td className="n">{num(m.roas)}</td>
                    <td className="n">{money(m.cpa)}</td>
                    <td className="n">${num(m.epc)}</td>
                    <td className="n">{trend(m.roas_trend_pct)}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span className={`decision-pill ${d.decision}`}>
                          <span className="dot"></span>
                          {d.decision}
                        </span>
                        <span className="conf">{d.confidence}</span>
                      </div>
                    </td>
                  </tr>
                  {open === k && (
                    <tr className="detail">
                      <td colSpan="8"><RowDetail decision={d} metric={m} /></td>
                    </tr>
                  )}
                </Fragment>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
