export default function VerdictBanner({ summary }) {
  const money = (n) => `$${Math.round(n || 0).toLocaleString()}`
  return (
    <div className="verdict fade">
      <div className="micro">Morning brief</div>
      <div className="lead">
        Analyzed <b>{summary.entities}</b> ad sets across <b>{summary.platforms}</b> platform{summary.platforms === 1 ? '' : 's'}.
        {' '}<b>{summary.scale}</b> to scale, <b>{summary.kill}</b> to kill, <b>{summary.watch}</b> to watch —
        {' '}about <b>{money(summary.wasted_daily_spend)}/day</b> going to underperformers.
      </div>
      <div className="stats">
        <div className="stat"><div className="num scale">{summary.scale}</div><div className="lbl">Scale</div></div>
        <div className="stat"><div className="num kill">{summary.kill}</div><div className="lbl">Kill</div></div>
        <div className="stat"><div className="num">{summary.watch}</div><div className="lbl">Watch</div></div>
        <div className="stat"><div className="num kill">{money(summary.wasted_daily_spend)}</div><div className="lbl">Wasted / day</div></div>
        <div className="stat"><div className="num">{money(summary.total_daily_spend)}</div><div className="lbl">Total / day</div></div>
      </div>
    </div>
  )
}
