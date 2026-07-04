export default function VerdictBanner({ summary }) {
  const money = (n) => `$${Math.round(n || 0).toLocaleString()}`
  return (
    <div className="verdict fade">
      <div className="verdict-accent-bar">
        <div className="g"></div>
        <div className="a"></div>
        <div className="r"></div>
      </div>
      <div className="micro">Morning brief</div>
      <div className="lead">
        Analyzed <b className="accent">{summary.entities}</b> ad sets across <b className="accent">{summary.platforms}</b> platform{summary.platforms === 1 ? '' : 's'}.
        {' '}<b className="accent">{summary.scale}</b> to scale, <b className="accent">{summary.kill}</b> to kill, <b className="accent">{summary.watch}</b> to watch —
        {' '}about <b className="kill">{money(summary.wasted_daily_spend)}/day</b> going to underperformers.
      </div>
      <div className="stats">
        <div className="stat">
          <div className="stat-header">
            <div className="stat-dot scale"></div><div className="lbl">Scale</div>
          </div>
          <div className="num scale">{summary.scale}</div>
        </div>
        <div className="stat">
          <div className="stat-header">
            <div className="stat-dot kill"></div><div className="lbl">Kill</div>
          </div>
          <div className="num kill">{summary.kill}</div>
        </div>
        <div className="stat">
          <div className="stat-header">
            <div className="stat-dot watch"></div><div className="lbl">Watch</div>
          </div>
          <div className="num">{summary.watch}</div>
        </div>
        <div className="stat">
          <div className="stat-header">
            <div className="stat-dot wasted"></div><div className="lbl">Wasted / day</div>
          </div>
          <div className="num kill">{money(summary.wasted_daily_spend)}</div>
        </div>
        <div className="stat">
          <div className="stat-header">
            <div className="stat-dot total"></div><div className="lbl">Total / day</div>
          </div>
          <div className="num">{money(summary.total_daily_spend)}</div>
        </div>
      </div>
    </div>
  )
}
